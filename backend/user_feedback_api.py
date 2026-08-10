"""
User Feedback API for Dragon KARAU AI
Task 25: User feedback collection, rating system, issue reporting
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()
logger = logging.getLogger(__name__)


class UserFeedbackAPI:
    """User feedback collection and management system"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        self.feedback_categories = [
            'station_quality', 'app_performance', 'feature_request',
            'bug_report', 'content_issue', 'general'
        ]
        
        self.priority_levels = {
            'critical': {'score': 5, 'response_time_hours': 4},
            'high': {'score': 4, 'response_time_hours': 24},
            'medium': {'score': 3, 'response_time_hours': 72},
            'low': {'score': 2, 'response_time_hours': 168},
            'info': {'score': 1, 'response_time_hours': 336}
        }
        
        logger.info("User Feedback API initialized")
    
    async def run_feedback_cycle(self) -> Dict[str, Any]:
        """Run complete feedback processing cycle"""
        start_time = datetime.utcnow()
        
        logger.info("💬 Starting User Feedback Cycle")
        
        results = {
            'timestamp': start_time.isoformat(),
            'processing': {},
            'analytics': {}
        }
        
        # Process feedback
        results['processing']['new_feedback'] = await self.process_new_feedback()
        results['processing']['pending_issues'] = await self.process_pending_issues()
        results['analytics']['sentiment'] = await self.analyze_feedback_sentiment()
        results['analytics']['trends'] = await self.identify_feedback_trends()
        
        # Generate insights
        results['insights'] = await self.generate_feedback_insights()
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        results['execution_time_seconds'] = duration
        results['status'] = 'completed'
        
        # Store results
        await self.db.feedback_cycle_history.insert_one(results.copy())
        
        logger.info(f"✅ Feedback Cycle Complete: {duration:.2f}s")
        
        return results
    
    async def submit_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit user feedback"""
        try:
            feedback = {
                'user_id': feedback_data.get('user_id'),
                'category': feedback_data.get('category', 'general'),
                'title': feedback_data.get('title'),
                'description': feedback_data.get('description'),
                'rating': feedback_data.get('rating'),  # 1-5 stars
                'station_id': feedback_data.get('station_id'),  # If feedback about specific station
                'metadata': feedback_data.get('metadata', {}),  # Device info, app version, etc.
                'status': 'new',
                'priority': self._calculate_priority(feedback_data),
                'created_at': datetime.utcnow(),
                'resolved': False,
                'responses': []
            }
            
            # Validate category
            if feedback['category'] not in self.feedback_categories:
                return {'status': 'error', 'error': f'Invalid category. Must be one of: {self.feedback_categories}'}
            
            result = await self.db.user_feedback.insert_one(feedback)
            feedback['_id'] = str(result.inserted_id)
            
            logger.info(f"Feedback submitted: {feedback['category']} - {feedback['priority']}")
            
            # Auto-respond based on priority
            if feedback['priority'] in ['critical', 'high']:
                await self._send_auto_response(str(result.inserted_id))
            
            return {
                'status': 'success',
                'feedback_id': str(result.inserted_id),
                'message': 'Feedback submitted successfully',
                'priority': feedback['priority']
            }
            
        except Exception as e:
            logger.error(f"Feedback submission error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _calculate_priority(self, feedback_data: Dict[str, Any]) -> str:
        """Calculate feedback priority"""
        category = feedback_data.get('category', 'general')
        rating = feedback_data.get('rating', 3)
        
        # Critical priority
        if category == 'bug_report' and rating <= 2:
            return 'critical'
        if category == 'content_issue':
            return 'high'
        
        # High priority
        if rating <= 2:
            return 'high'
        if category == 'feature_request' and rating >= 4:
            return 'medium'
        
        # Medium priority
        if rating == 3:
            return 'medium'
        
        # Low priority
        if rating >= 4:
            return 'low'
        
        return 'info'
    
    async def _send_auto_response(self, feedback_id: str) -> None:
        """Send automatic response to user"""
        try:
            response = {
                'message': 'Thank you for your feedback. We are reviewing your issue and will respond shortly.',
                'responder': 'system',
                'timestamp': datetime.utcnow()
            }
            
            await self.db.user_feedback.update_one(
                {'_id': ObjectId(feedback_id)},
                {'$push': {'responses': response}, '$set': {'status': 'acknowledged'}}
            )
        except Exception as e:
            logger.error(f"Auto-response error: {e}")
    
    async def rate_station(self, user_id: str, station_id: str, rating: int, review: Optional[str] = None) -> Dict[str, Any]:
        """Rate a radio station"""
        try:
            if not 1 <= rating <= 5:
                return {'status': 'error', 'error': 'Rating must be between 1 and 5'}
            
            rating_doc = {
                'user_id': user_id,
                'station_id': station_id,
                'rating': rating,
                'review': review,
                'created_at': datetime.utcnow()
            }
            
            # Insert rating
            await self.db.station_ratings.insert_one(rating_doc)
            
            # Update station's average rating
            await self._update_station_rating(station_id)
            
            return {
                'status': 'success',
                'message': 'Rating submitted successfully',
                'rating': rating
            }
            
        except Exception as e:
            logger.error(f"Station rating error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _update_station_rating(self, station_id: str) -> None:
        """Update station's average rating"""
        try:
            # Calculate average rating
            pipeline = [
                {'$match': {'station_id': station_id}},
                {'$group': {
                    '_id': '$station_id',
                    'avg_rating': {'$avg': '$rating'},
                    'total_ratings': {'$sum': 1}
                }}
            ]
            
            result = await self.db.station_ratings.aggregate(pipeline).to_list(length=1)
            
            if result:
                avg_rating = result[0]['avg_rating']
                total_ratings = result[0]['total_ratings']
                
                await self.db.radio_stations.update_one(
                    {'_id': ObjectId(station_id)},
                    {'$set': {
                        'user_rating': round(avg_rating, 2),
                        'total_ratings': total_ratings,
                        'rating_updated_at': datetime.utcnow()
                    }}
                )
        except Exception as e:
            logger.error(f"Update station rating error: {e}")
    
    async def report_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Report an issue"""
        try:
            issue = {
                'user_id': issue_data.get('user_id'),
                'type': issue_data.get('type', 'bug'),  # bug, content, quality, other
                'title': issue_data.get('title'),
                'description': issue_data.get('description'),
                'station_id': issue_data.get('station_id'),
                'severity': issue_data.get('severity', 'medium'),
                'status': 'open',
                'created_at': datetime.utcnow(),
                'resolved': False,
                'resolution': None
            }
            
            result = await self.db.issue_reports.insert_one(issue)
            
            # Auto-flag station if multiple reports
            if issue.get('station_id'):
                await self._check_station_reports(issue['station_id'])
            
            return {
                'status': 'success',
                'issue_id': str(result.inserted_id),
                'message': 'Issue reported successfully'
            }
            
        except Exception as e:
            logger.error(f"Issue report error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _check_station_reports(self, station_id: str) -> None:
        """Check if station has multiple reports and flag if needed"""
        try:
            report_count = await self.db.issue_reports.count_documents({
                'station_id': station_id,
                'resolved': False
            })
            
            # Flag station if 3+ unresolved reports
            if report_count >= 3:
                await self.db.radio_stations.update_one(
                    {'_id': ObjectId(station_id)},
                    {'$set': {
                        'status': 'flagged',
                        'flag_reason': f'{report_count} unresolved user reports',
                        'flagged_at': datetime.utcnow()
                    }}
                )
                logger.info(f"Station {station_id} flagged due to {report_count} reports")
        except Exception as e:
            logger.error(f"Check station reports error: {e}")
    
    async def process_new_feedback(self) -> Dict[str, Any]:
        """Process new feedback submissions"""
        try:
            new_feedback = await self.db.user_feedback.find({
                'status': 'new'
            }).to_list(length=100)
            
            processed = 0
            
            for feedback in new_feedback:
                # Auto-categorize and prioritize
                await self.db.user_feedback.update_one(
                    {'_id': feedback['_id']},
                    {'$set': {
                        'status': 'processing',
                        'processed_at': datetime.utcnow()
                    }}
                )
                processed += 1
            
            return {
                'status': 'success',
                'new_feedback_count': len(new_feedback),
                'processed': processed
            }
            
        except Exception as e:
            logger.error(f"Process feedback error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def process_pending_issues(self) -> Dict[str, Any]:
        """Process pending issues"""
        try:
            pending = await self.db.issue_reports.count_documents({
                'status': 'open',
                'resolved': False
            })
            
            # Check for overdue issues
            overdue = await self.db.issue_reports.count_documents({
                'status': 'open',
                'created_at': {'$lt': datetime.utcnow() - timedelta(days=7)}
            })
            
            return {
                'status': 'success',
                'pending_issues': pending,
                'overdue_issues': overdue
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def analyze_feedback_sentiment(self) -> Dict[str, Any]:
        """Analyze overall feedback sentiment"""
        try:
            # Get recent feedback with ratings
            recent_feedback = await self.db.user_feedback.find({
                'created_at': {'$gte': datetime.utcnow() - timedelta(days=30)},
                'rating': {'$exists': True}
            }).to_list(length=1000)
            
            if not recent_feedback:
                return {'status': 'no_data', 'message': 'No recent feedback with ratings'}
            
            # Calculate sentiment
            ratings = [f['rating'] for f in recent_feedback if f.get('rating')]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            positive = len([r for r in ratings if r >= 4])
            neutral = len([r for r in ratings if r == 3])
            negative = len([r for r in ratings if r <= 2])
            
            sentiment = 'positive' if avg_rating >= 4 else ('neutral' if avg_rating >= 3 else 'negative')
            
            return {
                'status': 'success',
                'average_rating': round(avg_rating, 2),
                'sentiment': sentiment,
                'distribution': {
                    'positive': positive,
                    'neutral': neutral,
                    'negative': negative
                },
                'total_feedback': len(recent_feedback)
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def identify_feedback_trends(self) -> Dict[str, Any]:
        """Identify trends in user feedback"""
        try:
            # Analyze feedback by category
            pipeline = [
                {'$match': {
                    'created_at': {'$gte': datetime.utcnow() - timedelta(days=30)}
                }},
                {'$group': {
                    '_id': '$category',
                    'count': {'$sum': 1},
                    'avg_rating': {'$avg': '$rating'}
                }},
                {'$sort': {'count': -1}}
            ]
            
            trends = await self.db.user_feedback.aggregate(pipeline).to_list(length=10)
            
            return {
                'status': 'success',
                'top_categories': [{
                    'category': t['_id'],
                    'count': t['count'],
                    'avg_rating': round(t.get('avg_rating', 0), 2) if t.get('avg_rating') else None
                } for t in trends]
            }
            
        except Exception as e:
            logger.error(f"Trend identification error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def generate_feedback_insights(self) -> Dict[str, Any]:
        """Generate actionable insights from feedback"""
        try:
            insights = []
            
            # Check for high-priority unresolved feedback
            critical_count = await self.db.user_feedback.count_documents({
                'priority': {'$in': ['critical', 'high']},
                'resolved': False
            })
            
            if critical_count > 0:
                insights.append({
                    'type': 'action_required',
                    'message': f'{critical_count} high-priority feedback items need attention',
                    'severity': 'high'
                })
            
            # Check for negative trend
            sentiment = await self.analyze_feedback_sentiment()
            if sentiment.get('sentiment') == 'negative':
                insights.append({
                    'type': 'sentiment_alert',
                    'message': 'User sentiment is negative - requires investigation',
                    'severity': 'medium'
                })
            
            return {
                'status': 'success',
                'insights': insights,
                'total_insights': len(insights)
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics"""
        try:
            total = await self.db.user_feedback.count_documents({})
            resolved = await self.db.user_feedback.count_documents({'resolved': True})
            pending = await self.db.user_feedback.count_documents({'resolved': False})
            
            # Get recent feedback
            recent = await self.db.user_feedback.find({}).sort('created_at', -1).limit(10).to_list(length=10)
            
            return {
                'status': 'success',
                'total_feedback': total,
                'resolved': resolved,
                'pending': pending,
                'recent_feedback': [{
                    'id': str(f['_id']),
                    'category': f.get('category'),
                    'priority': f.get('priority'),
                    'rating': f.get('rating'),
                    'created_at': f.get('created_at').isoformat() if f.get('created_at') else None
                } for f in recent]
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}


def get_user_feedback_api():
    """Get singleton user feedback API instance"""
    global _feedback_api
    if '_feedback_api' not in globals():
        globals()['_feedback_api'] = UserFeedbackAPI()
    return globals()['_feedback_api']
