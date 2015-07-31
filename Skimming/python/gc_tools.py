"""
Tools for integrating GC with python applications

:warning: Since an application on a remote system does not have access to the
	grid-control repository at runtime, it is mandatory to include the relevant
	functions in your own codebase.
"""

import difflib
import inspect
import linecache
import sys
import ast


NO_DEFAULT = object()


def gc_var_or_default(gc_var_name, default=NO_DEFAULT, gc_var_str="@", var_type=ast.literal_eval):
	"""
	Use an injected GridControl variable or fall back to a default

	This function can be used in place of any variable in the form
	``gc_var_or_default('@MU_COUNT@', 2)``. If GC replaces the variable
	in source code (e.g. a config), the call is implicitly changed to
	``gc_var_or_default('16', 2)`` which is detected by the function,
	yielding the new input.

	:param gc_var_name: name of the variable for GC, including GC variable strings
	:type gc_var_name: str, unicode
	:param default: value to use if no replacement by GC happened
	:param gc_var_str: the start/end string of GC the variable (e.g. ``"@"``)
	:type gc_var_str: str, unicode
	:param var_type: callable to convert literal to appropriate variable type
	:type var_type: callable

	:note: If var_type is not ``None``, it is automatically guessed using
		``type(default)``. The reverse does not hold true; if ``var_type`` is
		explicitly specified, ``default`` is not checked for type compatibility.

	:note: By convention from GC, gc_var_str should be ``"@"`` or ``"__"``. This
		is not enforced by the function.
	"""
	if gc_var_name.startswith(gc_var_str) and gc_var_name.endswith(gc_var_str):
		if default is NO_DEFAULT:
			raise TypeError("'%s' must be a GC variable/parameter (no default given as fallback)" % gc_var_name.strip(gc_var_str))
		return default
	var_type = type(default) if var_type is None else var_type
	if var_type is bool:
		return gc_var_name.lower() in ("true", "yes", "y", "1")
	return var_type(gc_var_name)

def gc_var_or_callable_parameter(gc_var_name, callable, gc_var_str="@", var_type=ast.literal_eval):
	"""
	Similar to :py:func:`~.gc_var_or_default`, extracting the default
	dynamically from a callable
	"""
	# extract callable signature
	args, _, _, defaults = inspect.getargspec(callable)
	# extract the variable name from the callstack
	call_frame = sys._getframe(1)
	var_assigned = False
	# variable assignment and name might be on different lines, so backtrack a little if needed
	for backtrack in range(8):
		call_line = linecache.getline(call_frame.f_code.co_filename, call_frame.f_lineno-backtrack).partition("#")[0].strip()
		# variable name is always before assignment operator
		if "=" in call_line:
			var_assigned = True
			call_line = call_line.partition("=")[0].strip()
		if var_assigned and call_line:
			var_name = call_line
			break
	else:
		raise ValueError("GC Tools failed to find variable name in calling frame")
	try:
		return gc_var_or_default(
			gc_var_name,
			default=defaults[args.index(var_name)-len(args)],
			gc_var_str=gc_var_str,
			var_type=var_type
		)
	except IndexError:
		# parameter BEFORE defaulting ones -> no default
		return gc_var_or_default(
			gc_var_name,
			gc_var_str=gc_var_str,
			var_type=var_type
		)

