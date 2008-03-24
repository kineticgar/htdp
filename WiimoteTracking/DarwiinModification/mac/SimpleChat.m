#import "SimpleChat.h"
#import "NetSocket.h"
#import "AppController.h"

@implementation SimpleChat

- (id)initWithNetSocket:(NetSocket*)inNetSocket
{
	if( ![super init] ) {
		return nil;
	}
	
	PORT = 4440;   // arbitrary port#
	mSocket = [[NetSocket netsocketConnectedToHost:@"localhost" port:PORT] retain];
	//NSLog(@"Connecting...");
	[mSocket scheduleOnCurrentRunLoop];
	[mSocket setDelegate:self];
	return self;
}


- (void)connect:(id)sender
{
	mSocket = [[NetSocket netsocketConnectedToHost:@"localhost" port:44100] retain];
	[mSocket scheduleOnCurrentRunLoop];
	[mSocket setDelegate:self];
}


- (IBAction)sendChat:(id)sender
{

}

- (void)netsocketConnected:(NetSocket*)inNetSocket
{
	//NSLog( @"Connected to Jmol" );
	//[mSocket writeString:@"hello world\n" encoding:NSASCIIStringEncoding];
}

- (void)netsocket:(NetSocket*)inNetSocket connectionTimedOut:(NSTimeInterval)inTimeout
{
	
}

- (void)netsocketDisconnected:(NetSocket*)inNetSocket
{
	//NSLog( @"Disconnected" );
}

- (void)netsocket:(NetSocket*)inNetSocket dataAvailable:(unsigned)inAmount
{
	//NSLog(@"Data available");
	NSString* in = [mSocket readString:NSASCIIStringEncoding amount:inAmount];
	incomingMouseMode = [in intValue];
	//NSLog(@"incomingMouseMode: %@\n", incomingMouseMode);
	
}

- (void)netsocketDataSent:(NetSocket*)inNetSocket
{
	//NSLog(@"Data sent");
}

- (void)sendScript:(NSString*)script
{
	// sends the script over to Jmol
	[mSocket writeString:script encoding:NSASCIIStringEncoding];
}

- (void)setMouseMode:(int)mode
{
	incomingMouseMode = mode;
}
- (int)getMouseMode;
{
	return incomingMouseMode;
}

@end
