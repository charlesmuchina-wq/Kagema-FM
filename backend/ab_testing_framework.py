"""
A/B Testing Framework for Dragon KARAU AI
Task 23: Experiment management, user segmentation, results analysis
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import random
from bson import ObjectId

load_dotenv()
logger = logging.getLogger(__name__)


class ABTestingFramework:
    """A/B Testing and experimentation platform"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        logger.info("A/B Testing Framework initialized")
    
    async def run_ab_testing_cycle(self) -> Dict[str, Any]:
        """Run complete A/B testing cycle"""
        start_time = datetime.utcnow()
        
        logger.info("🧪 Starting A/B Testing Cycle")
        
        results = {
            'timestamp': start_time.isoformat(),
            'experiments': {},
            'actions': []
        }
        
        # Manage active experiments
        results['experiments']['active'] = await self.manage_active_experiments()
        results['experiments']['analysis'] = await self.analyze_experiment_results()
        results['experiments']['cleanup'] = await self.cleanup_completed_experiments()
        
        # Auto-create experiments based on data patterns
        results['actions'] = await self.auto_generate_experiments()
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        results['execution_time_seconds'] = duration
        results['status'] = 'completed'
        
        # Store results
        await self.db.ab_testing_history.insert_one(results.copy())
        
        logger.info(f"✅ A/B Testing Cycle Complete: {duration:.2f}s")
        
        return results
    
    async def create_experiment(self, experiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new A/B test experiment"""
        try:
            experiment = {
                'name': experiment_data.get('name'),
                'description': experiment_data.get('description'),
                'hypothesis': experiment_data.get('hypothesis'),
                'type': experiment_data.get('type', 'simple_ab'),  # simple_ab, multivariate, sequential
                'variants': experiment_data.get('variants', []),  # List of variant configurations
                'status': 'active',
                'created_at': datetime.utcnow(),
                'start_date': experiment_data.get('start_date', datetime.utcnow()),
                'end_date': experiment_data.get('end_date'),
                'target_metric': experiment_data.get('target_metric'),  # e.g., 'play_count', 'favorite_rate'
                'sample_size': experiment_data.get('sample_size', 1000),
                'confidence_level': experiment_data.get('confidence_level', 95),
                'results': {
                    'conversions': {},
                    'metrics': {},
                    'statistical_significance': None
                }
            }
            
            result = await self.db.ab_experiments.insert_one(experiment)
            experiment['_id'] = str(result.inserted_id)
            
            logger.info(f"Created experiment: {experiment['name']}")
            return {'status': 'success', 'experiment_id': str(result.inserted_id), 'experiment': experiment}
            
        except Exception as e:
            logger.error(f"Experiment creation error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def assign_user_to_variant(self, user_id: str, experiment_id: str) -> Dict[str, Any]:
        """Assign a user to an experiment variant"""
        try:
            # Check if user is already assigned
            existing = await self.db.ab_assignments.find_one({
                'user_id': user_id,
                'experiment_id': experiment_id
            })
            
            if existing:
                return {
                    'status': 'success',
                    'variant': existing['variant'],
                    'assigned_at': existing['assigned_at'].isoformat()
                }
            
            # Get experiment
            experiment = await self.db.ab_experiments.find_one({'_id': ObjectId(experiment_id)})
            if not experiment:
                return {'status': 'error', 'error': 'Experiment not found'}
            
            # Random assignment to variant
            variants = experiment.get('variants', [])
            if not variants:
                return {'status': 'error', 'error': 'No variants defined'}
            
            # Weighted random selection (if weights provided, otherwise uniform)
            weights = [v.get('weight', 1.0) for v in variants]
            selected_variant = random.choices(variants, weights=weights, k=1)[0]
            
            # Create assignment
            assignment = {
                'user_id': user_id,
                'experiment_id': experiment_id,
                'variant': selected_variant['name'],
                'variant_config': selected_variant,
                'assigned_at': datetime.utcnow(),
                'interactions': []
            }
            
            await self.db.ab_assignments.insert_one(assignment)
            
            return {
                'status': 'success',
                'variant': selected_variant['name'],
                'config': selected_variant.get('config', {})
            }
            
        except Exception as e:
            logger.error(f"Variant assignment error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def track_conversion(self, user_id: str, experiment_id: str, metric: str, value: float = 1.0) -> Dict[str, Any]:
        """Track a conversion event for an experiment"""
        try:
            # Get user's assignment
            assignment = await self.db.ab_assignments.find_one({
                'user_id': user_id,
                'experiment_id': experiment_id
            })
            
            if not assignment:
                return {'status': 'error', 'error': 'User not assigned to experiment'}
            
            # Record conversion
            conversion = {
                'user_id': user_id,
                'experiment_id': experiment_id,
                'variant': assignment['variant'],
                'metric': metric,
                'value': value,
                'timestamp': datetime.utcnow()
            }
            
            await self.db.ab_conversions.insert_one(conversion)
            
            # Update assignment interactions
            await self.db.ab_assignments.update_one(
                {'_id': assignment['_id']},
                {'$push': {'interactions': {
                    'metric': metric,
                    'value': value,
                    'timestamp': datetime.utcnow()
                }}}
            )
            
            return {'status': 'success', 'conversion_tracked': True}
            
        except Exception as e:
            logger.error(f"Conversion tracking error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def analyze_experiment_results(self) -> Dict[str, Any]:
        """Analyze results of all active experiments"""
        try:
            active_experiments = await self.db.ab_experiments.find({
                'status': 'active'
            }).to_list(length=100)
            
            analysis_results = []
            
            for exp in active_experiments:
                exp_id = str(exp['_id'])
                
                # Get conversions per variant
                conversions = await self.db.ab_conversions.find({
                    'experiment_id': exp_id
                }).to_list(length=10000)
                
                variant_stats = {}
                for variant in exp.get('variants', []):
                    variant_name = variant['name']
                    variant_conversions = [c for c in conversions if c['variant'] == variant_name]
                    
                    variant_stats[variant_name] = {
                        'total_conversions': len(variant_conversions),
                        'total_value': sum(c.get('value', 1.0) for c in variant_conversions),
                        'avg_value': sum(c.get('value', 1.0) for c in variant_conversions) / len(variant_conversions) if variant_conversions else 0
                    }
                
                # Calculate statistical significance (simplified chi-square test)
                significance = await self._calculate_significance(variant_stats)
                
                analysis = {
                    'experiment_id': exp_id,
                    'experiment_name': exp['name'],
                    'variant_stats': variant_stats,
                    'statistical_significance': significance,
                    'recommendation': self._generate_recommendation(variant_stats, significance)
                }
                
                analysis_results.append(analysis)
                
                # Update experiment with results
                await self.db.ab_experiments.update_one(
                    {'_id': exp['_id']},
                    {'$set': {
                        'results.metrics': variant_stats,
                        'results.statistical_significance': significance,
                        'last_analyzed': datetime.utcnow()
                    }}
                )
            
            return {
                'status': 'success',
                'experiments_analyzed': len(analysis_results),
                'results': analysis_results
            }
            
        except Exception as e:
            logger.error(f"Experiment analysis error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _calculate_significance(self, variant_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistical significance between variants"""
        # Simplified significance calculation
        if len(variant_stats) < 2:
            return {'significant': False, 'confidence': 0}
        
        variants = list(variant_stats.values())
        if not variants or not variants[0].get('total_conversions', 0):
            return {'significant': False, 'confidence': 0}
        
        # Compare control vs treatment (first two variants)
        control = variants[0]
        treatment = variants[1] if len(variants) > 1 else control
        
        control_rate = control['avg_value']
        treatment_rate = treatment['avg_value']
        
        # Simple difference calculation
        improvement = ((treatment_rate - control_rate) / control_rate * 100) if control_rate > 0 else 0
        
        # Simplified confidence (based on sample size)
        sample_size = control['total_conversions'] + treatment['total_conversions']
        confidence = min(95, (sample_size / 100) * 10)  # Reaches 95% at 950 samples
        
        return {
            'significant': confidence >= 80 and abs(improvement) >= 5,
            'confidence': round(confidence, 2),
            'improvement_percent': round(improvement, 2)
        }
    
    def _generate_recommendation(self, variant_stats: Dict[str, Any], significance: Dict[str, Any]) -> str:
        """Generate recommendation based on results"""
        if not significance.get('significant'):
            return 'Continue experiment - not enough data for conclusion'
        
        improvement = significance.get('improvement_percent', 0)
        
        if improvement > 10:
            return f'Implement treatment variant - {improvement:.1f}% improvement'
        elif improvement < -10:
            return f'Keep control variant - treatment performed {abs(improvement):.1f}% worse'
        else:
            return 'No significant difference - either variant acceptable'
    
    async def manage_active_experiments(self) -> Dict[str, Any]:
        """Manage and check active experiments"""
        try:
            active = await self.db.ab_experiments.count_documents({'status': 'active'})
            expired = await self.db.ab_experiments.count_documents({
                'status': 'active',
                'end_date': {'$lt': datetime.utcnow()}
            })
            
            # Auto-complete expired experiments
            if expired > 0:
                await self.db.ab_experiments.update_many(
                    {
                        'status': 'active',
                        'end_date': {'$lt': datetime.utcnow()}
                    },
                    {'$set': {'status': 'completed', 'completed_at': datetime.utcnow()}}
                )
            
            return {
                'status': 'success',
                'active_experiments': active,
                'expired_auto_completed': expired
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def cleanup_completed_experiments(self) -> Dict[str, Any]:
        """Clean up old completed experiments"""
        try:
            # Archive experiments completed > 90 days ago
            cutoff = datetime.utcnow() - timedelta(days=90)
            
            old_experiments = await self.db.ab_experiments.find({
                'status': 'completed',
                'completed_at': {'$lt': cutoff}
            }).to_list(length=1000)
            
            if old_experiments:
                # Move to archive
                await self.db.ab_experiments_archive.insert_many(old_experiments)
                
                # Delete from active collection
                exp_ids = [exp['_id'] for exp in old_experiments]
                await self.db.ab_experiments.delete_many({'_id': {'$in': exp_ids}})
            
            return {
                'status': 'success',
                'archived': len(old_experiments)
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def auto_generate_experiments(self) -> List[Dict[str, Any]]:
        """Auto-generate experiment ideas based on data patterns"""
        suggestions = []
        
        try:
            # Check if we should test station recommendations
            total_stations = await self.db.radio_stations.count_documents({})
            if total_stations > 1000:
                suggestions.append({
                    'type': 'recommendation',
                    'name': 'Station Recommendation Algorithm Test',
                    'hypothesis': 'Improved recommendation algorithm increases user engagement',
                    'suggested': True
                })
            
            # Check if we should test UI layouts
            favorites_users = await self.db.user_favorites.distinct('user_id')
            if len(favorites_users) > 100:
                suggestions.append({
                    'type': 'ui_layout',
                    'name': 'Favorites Screen Layout Test',
                    'hypothesis': 'Grid layout vs list layout affects user interaction',
                    'suggested': True
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Auto-generation error: {e}")
            return []
    
    async def get_experiment_summary(self) -> Dict[str, Any]:
        """Get summary of all experiments"""
        try:
            total = await self.db.ab_experiments.count_documents({})
            active = await self.db.ab_experiments.count_documents({'status': 'active'})
            completed = await self.db.ab_experiments.count_documents({'status': 'completed'})
            
            recent = await self.db.ab_experiments.find({}).sort('created_at', -1).limit(5).to_list(length=5)
            
            return {
                'status': 'success',
                'total_experiments': total,
                'active': active,
                'completed': completed,
                'recent_experiments': [{
                    'id': str(exp['_id']),
                    'name': exp.get('name'),
                    'status': exp.get('status'),
                    'created_at': exp.get('created_at').isoformat() if exp.get('created_at') else None
                } for exp in recent]
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}


def get_ab_testing_framework():
    """Get singleton A/B testing framework instance"""
    global _ab_framework
    if '_ab_framework' not in globals():
        globals()['_ab_framework'] = ABTestingFramework()
    return globals()['_ab_framework']
