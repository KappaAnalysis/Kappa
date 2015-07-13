"""
Tools for integrating GC with python applications

:warning: Since an application on a remote system does not have access to the
	grid-control repository at runtime, it is mandatory to include the relevant
	functions in your own codebase.
"""

import difflib
import inspect


NO_DEFAULT = object()


def gc_var_or_default(gc_var_name, default=NO_DEFAULT, gc_var_str="@", var_type=None):
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

	:note: If var_type is not given or is ``None``, it is automatically
		guessed using ``type(default)``. The reverse does not hold true; if
		``var_type`` is explicitly specified, ``default`` is not checked for
		type compatibility.

	:note: By convention from GC, gc_var_str should be ``"@"`` or ``"__"``. This
		is not enforced by the function.
	"""
	if gc_var_name.startswith(gc_var_str) and gc_var_name.endswith(gc_var_str):
		if default is NO_DEFAULT:
			raise TypeError("'%s' must be a GC variable/parameter (no default given as fallback)" % gc_var_name.strip(gc_var_str))
		return default
	var_type = type(default) if var_type is None else var_type
	return var_type(gc_var_name)

def gc_var_or_callable_parameter(gc_var_name, callable, gc_var_str="@", var_type=None, var_name=None):
	"""
	Similar to :py:func:`~.gc_var_or_default`, extracting the default
	dynamically from a callable

	This function tries to find the parameter corresponding to the variable with
	the following steps performed for ``var_name``:

	1. ``var_name`` has been specified and names a parameter to ``callable``

	2. ``gc_var_name`` without ``gc_var_str`` is tried as ``var_name``

	3. match without any ``_``

	4. match as lowercase

	5. match without any ``_`` and as lowercase

	6. best lowercase match of both ``var_name`` and parameters according to
		:py:func:`difflib.get_close_matches`
	"""
	args, _, _, defaults = inspect.getargspec(callable)
	if var_name not in args:
		var_name = gc_var_name.strip(gc_var_str)
		if var_name not in args:
			if var_name.replace("_", "") in args:
				var_name = var_name.replace("_", "")
			elif var_name.lower() in args:
				var_name = var_name.lower()
			elif var_name.lower().replace("_", "") in args:
				var_name = var_name.lower()
			else:
				args = [arg.lower() for arg in args]
				matches = difflib.get_close_matches(var_name.lower(), args)
				if not matches:
					raise ValueError("Failed to guess parameter corresponding to GC variable '%s'"%gc_var_name.strip(gc_var_str))
				var_name = matches[0]
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

