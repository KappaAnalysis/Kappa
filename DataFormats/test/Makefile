CXX      = g++
CXXFLAGS = -O2 -Wall -fPIC $(shell root-config --cflags)

LD       = g++
LDFLAGS  = -O $(shell root-config --libs) $(SYSLIBS) \
	-lGenVector -lReflex -lMathMore -lMathCore -lReflexDict

PROGRAM = dict.so
all: $(PROGRAM)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $<

%.so: %.o
	$(LD) -shared $(LDFLAGS) -o $@ $^

dict.cpp: standalone.h ../src/classes.h LinkDef.h
	rootcint -f $@ -c $^

install: $(PROGRAM)
	test -d "$(MYPREFIX)/lib"
	[ -n "$(filter %.a %.so, $(PROGRAM))" ] && \
		cp $(filter %.a %.so, $(PROGRAM)) "$(MYPREFIX)/lib" \
		|| true

clean:
	@rm -f *.o *.so dict.*
