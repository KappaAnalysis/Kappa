PROGRAM  = libKappa.so libKappa.a libKappa.o

CXX      = g++
CXXFLAGS = -O2 -Wall -fPIC $(shell root-config --cflags)
LDFLAGS  = -O $(shell root-config --libs) $(SYSLIBS) \
	-lGenVector -lReflex -lMathCore -lReflexDict

all: $(PROGRAM)

%.o: %.cpp KDebug.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $<

%.a: %.o KDebug.o
	ar rcs $@ $^

%.so: %.o KDebug.o
	$(CXX) $(LDFLAGS) -shared -o $@ $^

libKappa.cpp: standalone.h ../src/classes.h LinkDef.h
	rootcint -f $@ -c $^

install: $(PROGRAM)
	test -d "$(MYPREFIX)/lib"
	[ -n "$(filter %.a %.so, $(PROGRAM))" ] && \
		cp $(filter %.a %.so, $(PROGRAM)) "$(MYPREFIX)/lib" \
		|| true

clean:
	@rm -f libKappa.*
