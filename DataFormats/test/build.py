#!/usr/bin/env pyrate

build_output = ['makefile', 'ninja']
root = find_external('root')
kappa_dict = root.dictionary('libKappa', 'standalone.h ../src/classes.h LinkDef.h', include_list = ['../../..'])
kappa_dict_input = [kappa_dict, '../src/KDebug.cpp', root]
shared_library('libKappa', kappa_dict_input, compiler_opts = ['-O3 -I../../..'])
static_library('libKappa', kappa_dict_input, compiler_opts = ['-O3 -I../../..'])
