INCPATH = -I./opencv/include/opencv
LIBPATH = -L./opencv/lib/
OPTIONS = -lcv -lcvaux -lcxcore -lhighgui -lstdc++ -Wl,--rpath -Wl,./opencv/lib/
%:%.cpp
	g++ $(INCPATH) $(LIBPATH) $(OPTIONS) $^ -o $@
