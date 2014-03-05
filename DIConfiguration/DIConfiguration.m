//
//  DIConfiguration.m
//  DIConfiguration
//
//  Copyright (c) 2014 Utah Street Labs, Inc. All rights reserved.
//

#import "DIConfiguration.h"

static NSDictionary *defaults;
static NSDictionary *environment;

@implementation DIConfiguration

// Inspired by http://blog.carbonfive.com/2011/06/20/managing-ios-configurations-per-environment-in-xcode-4/
// Load two dictionaries: a per-configuration dictionary (Debug, Staging, Release, etc) and a defaults
// dictionary. Look for the given property in the per-configuration dictionary first and fall back to the defaults
// dictionary if the value is not found.
//
// The per-configuration dictionary's key can be overridden at runtime by setting the ENVIRONMENT environment variable
// in the run scheme. We use this to create per-developer environments.
+ prop:(NSString *)name {
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        NSString *envsPListPath = [[NSBundle mainBundle] pathForResource:@"Environments" ofType:@"plist"];
        NSDictionary *environments = [[NSDictionary alloc] initWithContentsOfFile:envsPListPath];
        NSString* environmentName = [[[NSBundle mainBundle] infoDictionary] objectForKey:@"Configuration"];
        environment = [environments objectForKey:environmentName];
        if (!environment) DI_LOG(@"WARNING: could not find config for %@ in %@", environmentName, environments);
        defaults = [environments objectForKey:@"Defaults"];
    });
    NSString *value = environment[name];
    if (!value) value = defaults[name];
    if (!value) DI_LOG(@"WARNING: configuration key %@ is not defined", name);
    return value;
}

@end
