
#include <OpenCV/OpenCV.h>
#include <cassert>
#include <iostream>
#include <stdio.h>


const CFIndex CASCADE_NAME_LEN = 2048;
      char    CASCADE_NAME[CASCADE_NAME_LEN] = "haarcascade_frontalface_alt2.xml"; // this is a dummy

using namespace std;

int main (int argc, char * const argv[]) 
{
    const int scale = 2;
	
	const int static_center_x = 320;
	const int static_center_y = 240;
	
	double PI = 3.14159265358979;
	double FOV = 40; // Should be roughly 54.3...but I guess the listed stats are bogus
	double RAD_PER_PIXEL = (PI*(FOV/180)) / 640; // Image is 640 x 480
	double REAL_RADIUS = 10.4;
	double DISTANCE_FACTOR = 4626;

    // locate haar cascade from inside application bundle
    // (this is the mac way to package application resources)
    CFBundleRef mainBundle  = CFBundleGetMainBundle ();
    assert (mainBundle);
    CFURLRef    cascade_url = CFBundleCopyResourceURL (mainBundle, CFSTR("haarcascade_frontalface_alt2"), CFSTR("xml"), NULL);
    assert (cascade_url);
    Boolean     got_it      = CFURLGetFileSystemRepresentation (cascade_url, true, 
                                                                reinterpret_cast<UInt8 *>(CASCADE_NAME), CASCADE_NAME_LEN);
    if (! got_it)
        abort ();
    
    // create all necessary instances
	CvCapture * camera = cvCreateCameraCapture (CV_CAP_ANY);
    CvHaarClassifierCascade* cascade = (CvHaarClassifierCascade*) cvLoad (CASCADE_NAME, 0, 0, 0);
    CvMemStorage* storage = cvCreateMemStorage(0);
    assert (storage);

    // you do own an iSight, don't you ?!?
    if (! camera)
        abort ();

    // did we load the cascade?!?
    if (! cascade)
        abort ();

    // get an initial frame and duplicate it for later work
    IplImage *  current_frame = cvQueryFrame (camera);
	IplImage *  gray_image    = cvCreateImage(cvSize (current_frame->width, current_frame->height), IPL_DEPTH_8U, 1);
    IplImage *  small_image   = cvCreateImage(cvSize (current_frame->width / scale, current_frame->height / scale), IPL_DEPTH_8U, 1);
    
	assert (current_frame && gray_image);
    
	
    // as long as there are images ...
    while (current_frame = cvQueryFrame (camera))
    {
        // convert to gray and downsize
        cvCvtColor (current_frame, gray_image, CV_BGR2GRAY);
        cvResize (gray_image, small_image, CV_INTER_LINEAR);
        
        // detect faces
        CvSeq* faces = cvHaarDetectObjects (small_image, cascade, storage,
        //                                    1.1, 2, CV_HAAR_DO_CANNY_PRUNING,
                                            1.2, 2, 0,
                                            cvSize (30, 30));
		
                
		double center_x = 0;
		double center_y = 0;
		double radius = 0;
		
		// If the faces were detected, and there's more than 0, just take the first one found
		for (int i = 0; i < (faces ? ((faces->total > 0) ? 1 : 0) : 0); i++)
        {
			
            CvRect* r = (CvRect*) cvGetSeqElem (faces, i);
            center_x = (small_image->width - r->width*0.5 - r->x) *scale;
            center_y = (r->y + r->height*0.5)*scale;
            radius = (r->width + r->height)*0.25*scale;
						
			double x_rad = RAD_PER_PIXEL * (static_center_x - center_x);
			double y_rad = RAD_PER_PIXEL * (static_center_y - center_y);
			double z_dist = DISTANCE_FACTOR / radius;
			//double z_dist = REAL_RADIUS / tan(radius * RAD_PER_PIXEL);
			
			printf("X%f;Y%f;Z%f;\n", x_rad, y_rad, z_dist);
			fflush(stdout);
			
			// Debug info
			//cout << "(" << center.x << "," << center.y << ") = " << radius << endl;
			
			
        }
	}
	
	printf("QUIT");
    
    // be nice and return no error
    return 0;
}
