PROGRAM  = libKappa.so libKappa.a libKappa.o

CXX      = g++
CXXFLAGS = -O2 -Wall -fPIC $(shell root-config --cflags) -I../../../
LDFLAGS  = -O $(shell root-config --libs) $(SYSLIBS) \
	-lGenVector -lReflex -lMathCore -lReflexDict

all: $(PROGRAM)

Hash.o: ../src/Hash.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $<

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $<

%.a: %.o KDebug.o
	ar rcs $@ $^
	mkdir -p ../../lib
	cp $@ ../../lib

%.so: %.o KDebug.o Hash.o
	$(CXX) $(LDFLAGS) -shared -o $@ $^
	mkdir -p ../../lib
	cp $@ ../../lib

%.sbin: %.o libKappa.o
	$(CXX) $(LDFLAGS) -o $@ $^

libKappa.cpp: standalone.h ../src/classes.h LinkDef.h
	rootcint -f $@ -c $^

install: $(PROGRAM)

clean:
	@rm -f *.o libKappa.* ../../lib/*
