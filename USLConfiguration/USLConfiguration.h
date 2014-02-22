//
//  USLConfiguration.h
//  USLConfiguration
//
//  Copyright (c) 2014 Utah Street Labs, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

#ifndef USL_LOG
#define USL_LOG NSLog
#endif

@interface USLConfiguration : NSObject
+ prop:(NSString *)name;
@end
