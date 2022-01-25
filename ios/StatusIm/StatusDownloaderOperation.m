#include "StatusDownloaderOperation.h"

@implementation StatusDownloaderOperation

- (void)URLSession:(NSURLSession *)session task:(NSURLSessionTask *)task didReceiveChallenge:(NSURLAuthenticationChallenge *)challenge completionHandler:(void (^)(NSURLSessionAuthChallengeDisposition disposition, NSURLCredential *credential))completionHandler {
  if ([challenge.protectionSpace.authenticationMethod isEqualToString:NSURLAuthenticationMethodServerTrust]) {
    //TODO: currently refuses ALL authentications, it should instead accept all system certs + our trusted cert
    NSURLSessionAuthChallengeDisposition disposition = NSURLSessionAuthChallengeCancelAuthenticationChallenge;

    //__block NSURLCredential *credential = nil;

    //credential = [NSURLCredential credentialForTrust:challenge.protectionSpace.serverTrust];
    //disposition = NSURLSessionAuthChallengeUseCredential;

    if (completionHandler) {
      completionHandler(disposition, nil);
    }
  } else {
    [super URLSession:session task:task didReceiveChallenge:challenge completionHandler:completionHandler];
  }
}

@end
