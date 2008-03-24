/* SimpleChat */

#import <Cocoa/Cocoa.h>
@class NetSocket;

@interface SimpleChat : NSObject
{
	//IBOutlet NSView *mChatTextView;
    //IBOutlet NSTextField *mInputView;
    //IBOutlet NSWindow *mWindow;
	NetSocket* mSocket;
	
	//====changed by wiiguys====
    int incomingMouseMode;    // variable to indicate mouse mode sent from Jmol
	int PORT;				  // starting PORT number
}
- (IBAction)sendChat:(id)sender;
- (id)initWithNetSocket:(NetSocket*)inNetSocket;
- (void)sendScript:(NSString*)script;
- (void)setMouseMode:(int)mode;
- (int)getMouseMode;
@end
