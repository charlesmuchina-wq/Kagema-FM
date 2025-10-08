# iOS Audio Input Picker Native Module Implementation

This document outlines the implementation of the AVInputPickerInteraction native module for the Kagema FM app.

## Overview

The AVInputPickerInteraction API is a new iOS feature that allows apps to present a native audio input picker without requiring users to navigate to System Settings. This provides a seamless experience for switching between audio devices like AirPods, speakers, and wired headphones.

## Native Module Structure

### 1. iOS Native Implementation (Objective-C/Swift)

```objective-c
// KagemaAudioInputPicker.h
#import <React/RCTBridgeModule.h>
#import <React/RCTEventEmitter.h>
#import <AVFoundation/AVFoundation.h>

@interface KagemaAudioInputPicker : RCTEventEmitter <RCTBridgeModule, AVInputPickerInteractionDelegate>

@property (nonatomic, strong) AVInputPickerInteraction *inputPickerInteraction;
@property (nonatomic, strong) AVAudioSession *audioSession;

@end
```

```objective-c
// KagemaAudioInputPicker.m
#import "KagemaAudioInputPicker.h"

@implementation KagemaAudioInputPicker

RCT_EXPORT_MODULE();

- (instancetype)init {
    self = [super init];
    if (self) {
        [self setupAudioSession];
        [self setupInputPickerInteraction];
    }
    return self;
}

- (void)setupAudioSession {
    self.audioSession = [AVAudioSession sharedInstance];
    
    NSError *error = nil;
    
    // Configure audio session category and options
    [self.audioSession setCategory:AVAudioSessionCategoryPlayback
                       withOptions:AVAudioSessionCategoryOptionAllowBluetooth |
                                  AVAudioSessionCategoryOptionAllowBluetoothA2DP |
                                  AVAudioSessionCategoryOptionAllowAirPlay
                             error:&error];
    
    if (error) {
        NSLog(@"Audio session configuration error: %@", error.localizedDescription);
    }
    
    // Activate the session
    [self.audioSession setActive:YES error:&error];
    
    if (error) {
        NSLog(@"Audio session activation error: %@", error.localizedDescription);
    }
}

- (void)setupInputPickerInteraction {
    if (@available(iOS 15.0, *)) {
        self.inputPickerInteraction = [[AVInputPickerInteraction alloc] init];
        self.inputPickerInteraction.delegate = self;
    }
}

RCT_EXPORT_METHOD(presentInputPicker:(RCTPromiseResolveBlock)resolve
                 rejecter:(RCTPromiseRejectBlock)reject) {
    
    if (@available(iOS 15.0, *)) {
        if (self.inputPickerInteraction) {
            dispatch_async(dispatch_get_main_queue(), ^{
                // Present the input picker
                [self.inputPickerInteraction present];
                resolve(@YES);
            });
        } else {
            reject(@"UNAVAILABLE", @"Input picker interaction not available", nil);
        }
    } else {
        reject(@"UNSUPPORTED", @"iOS 15.0+ required for AVInputPickerInteraction", nil);
    }
}

RCT_EXPORT_METHOD(getAvailableInputs:(RCTPromiseResolveBlock)resolve
                 rejecter:(RCTPromiseRejectBlock)reject) {
    
    NSArray<AVAudioSessionPortDescription *> *availableInputs = self.audioSession.availableInputs;
    NSMutableArray *inputs = [NSMutableArray array];
    
    for (AVAudioSessionPortDescription *input in availableInputs) {
        NSDictionary *inputInfo = @{
            @"id": input.UID,
            @"name": input.portName,
            @"type": [self mapPortTypeToString:input.portType],
            @"isSelected": @([input.UID isEqualToString:self.audioSession.currentRoute.inputs.firstObject.UID])
        };
        [inputs addObject:inputInfo];
    }
    
    resolve(inputs);
}

RCT_EXPORT_METHOD(selectInput:(NSString *)inputId
                 resolver:(RCTPromiseResolveBlock)resolve
                 rejecter:(RCTPromiseRejectBlock)reject) {
    
    NSArray<AVAudioSessionPortDescription *> *availableInputs = self.audioSession.availableInputs;
    
    for (AVAudioSessionPortDescription *input in availableInputs) {
        if ([input.UID isEqualToString:inputId]) {
            NSError *error = nil;
            [self.audioSession setPreferredInput:input error:&error];
            
            if (error) {
                reject(@"SELECTION_FAILED", error.localizedDescription, error);
            } else {
                resolve(@YES);
            }
            return;
        }
    }
    
    reject(@"INPUT_NOT_FOUND", @"Audio input not found", nil);
}

- (NSString *)mapPortTypeToString:(AVAudioSessionPort)portType {
    if ([portType isEqualToString:AVAudioSessionPortBuiltInSpeaker]) {
        return @"builtin";
    } else if ([portType isEqualToString:AVAudioSessionPortBluetoothA2DP] ||
               [portType isEqualToString:AVAudioSessionPortBluetoothLE] ||
               [portType isEqualToString:AVAudioSessionPortBluetoothHFP]) {
        return @"bluetooth";
    } else if ([portType isEqualToString:AVAudioSessionPortAirPlay]) {
        return @"airplay";
    } else if ([portType isEqualToString:AVAudioSessionPortHeadphones] ||
               [portType isEqualToString:AVAudioSessionPortHeadsetMic]) {
        return @"wired";
    } else {
        return @"other";
    }
}

// AVInputPickerInteractionDelegate methods
- (void)inputPickerInteractionWillPresent:(AVInputPickerInteraction *)interaction API_AVAILABLE(ios(15.0)) {
    [self sendEventWithName:@"AudioInputPickerWillPresent" body:@{}];
}

- (void)inputPickerInteractionDidPresent:(AVInputPickerInteraction *)interaction API_AVAILABLE(ios(15.0)) {
    [self sendEventWithName:@"AudioInputPickerDidPresent" body:@{}];
}

- (void)inputPickerInteractionWillDismiss:(AVInputPickerInteraction *)interaction API_AVAILABLE(ios(15.0)) {
    [self sendEventWithName:@"AudioInputPickerWillDismiss" body:@{}];
}

- (void)inputPickerInteractionDidDismiss:(AVInputPickerInteraction *)interaction API_AVAILABLE(ios(15.0)) {
    [self sendEventWithName:@"AudioInputPickerDidDismiss" body:@{}];
}

- (NSArray<NSString *> *)supportedEvents {
    return @[
        @"AudioInputPickerWillPresent",
        @"AudioInputPickerDidPresent", 
        @"AudioInputPickerWillDismiss",
        @"AudioInputPickerDidDismiss",
        @"AudioInputChanged"
    ];
}

@end
```

### 2. Native Module Registration

```javascript
// metro.config.js - Add native module resolver
const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Add native module paths
config.resolver.platforms = ['ios', 'android', 'native', 'web'];

module.exports = config;
```

### 3. TypeScript Bridge

```typescript
// NativeAudioInputPicker.ts
import { NativeModules, NativeEventEmitter, Platform } from 'react-native';

interface AudioInputDevice {
  id: string;
  name: string;
  type: 'builtin' | 'bluetooth' | 'airplay' | 'wired' | 'other';
  isSelected: boolean;
}

interface NativeAudioInputPickerInterface {
  presentInputPicker(): Promise<boolean>;
  getAvailableInputs(): Promise<AudioInputDevice[]>;
  selectInput(inputId: string): Promise<boolean>;
}

const { KagemaAudioInputPicker } = NativeModules;

const NativeAudioInputPicker: NativeAudioInputPickerInterface = Platform.select({
  ios: KagemaAudioInputPicker,
  default: {
    presentInputPicker: () => Promise.reject('iOS only'),
    getAvailableInputs: () => Promise.reject('iOS only'),
    selectInput: () => Promise.reject('iOS only'),
  },
});

// Event emitter for native events
let eventEmitter: NativeEventEmitter | null = null;
if (Platform.OS === 'ios' && KagemaAudioInputPicker) {
  eventEmitter = new NativeEventEmitter(KagemaAudioInputPicker);
}

export { NativeAudioInputPicker, eventEmitter };
export type { AudioInputDevice };
```

## Implementation Steps

### Phase 1: Basic Setup
1. Create native module files in `ios/` directory
2. Add module to `ios/KagemaFM.xcodeproj`
3. Configure audio session in native code
4. Test basic module registration

### Phase 2: AVInputPickerInteraction Implementation
1. Implement `setupInputPickerInteraction` method
2. Add delegate methods for picker events
3. Implement `presentInputPicker` export method
4. Test native picker presentation

### Phase 3: Audio Input Management
1. Implement `getAvailableInputs` method
2. Add `selectInput` method for programmatic selection
3. Add audio route change notifications
4. Test input switching functionality

### Phase 4: Integration & Testing
1. Update TypeScript service to use native module
2. Test on physical iOS devices with different audio inputs
3. Verify AirPods, Bluetooth, and wired headphone switching
4. Add error handling and fallback mechanisms

## Configuration Requirements

### Info.plist Additions
```xml
<key>NSBluetoothAlwaysUsageDescription</key>
<string>Kagema FM needs Bluetooth access to detect and switch between audio devices like AirPods and speakers.</string>

<key>NSBluetoothPeripheralUsageDescription</key>
<string>Kagema FM needs Bluetooth access to connect to audio devices.</string>
```

### Build Settings
- Minimum iOS version: 15.0 (for AVInputPickerInteraction)
- Audio framework linking: AVFoundation.framework
- Background audio capabilities enabled

## Benefits

1. **Seamless UX**: Users can switch audio outputs without leaving the app
2. **Native Integration**: Uses Apple's official API for consistent behavior
3. **Car Integration**: Essential for CarPlay and automotive environments
4. **Accessibility**: Improves accessibility for users with hearing devices

## Testing Strategy

1. **Unit Tests**: Test native module methods and TypeScript bridge
2. **Integration Tests**: Test with different audio device configurations
3. **Device Testing**: Test on iPhone, iPad, CarPlay with various audio devices
4. **Edge Cases**: Test behavior with no available inputs, permission issues

This implementation provides a complete foundation for integrating AVInputPickerInteraction into the Kagema FM app, following iOS best practices and Apple's Human Interface Guidelines.