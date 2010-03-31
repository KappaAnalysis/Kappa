CXX      = g++
CXXFLAGS = -O2 -Wall -fPIC $(shell ${ROOTSYS}/bin/root-config --cflags)

LD       = g++
LDFLAGS  = -O $(shell ${ROOTSYS}/bin/root-config --libs) $(SYSLIBS) \
	-lGenVector -lReflex -lMathMore -lMathCore -lReflexDict

PROGRAM = dict.so
all: $(PROGRAM)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $<

%.so: %.o
	$(LD) -shared $(LDFLAGS) -o $@ $^

dict.cpp: ../src/classes.h LinkDef.h
	rootcint -f $@ -c $^

install: $(PROGRAM)
	test -d "$(MYPREFIX)/lib"
	[ -n "$(filter %.a %.so, $(PROGRAM))" ] && \
		cp $(filter %.a %.so, $(PROGRAM)) "$(MYPREFIX)/lib" \
		|| true
	test -d "$(MYPREFIX)/bin"
	[ -n "$(filter %.exe %.bin, $(PROGRAM))" ] && \
		cp -S=V $(filter %.exe %.bin, $(PROGRAM)) "$(MYPREFIX)/bin" \
		|| true

clean:
	@rm -f *.o *.so dict.*
