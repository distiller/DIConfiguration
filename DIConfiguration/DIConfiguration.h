//
//  DIConfiguration.h
//  DIConfiguration
//
//  Copyright (c) 2014 Utah Street Labs, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

#ifndef DI_LOG
#define DI_LOG NSLog
#endif

@interface DIConfiguration : NSObject
+ prop:(NSString *)name;
@end
