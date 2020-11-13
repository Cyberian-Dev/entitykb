
(function(l, r) { if (l.getElementById('livereloadscript')) return; r = l.createElement('script'); r.async = 1; r.src = '//' + (window.location.host || 'localhost').split(':')[0] + ':35729/livereload.js?snipver=1'; r.id = 'livereloadscript'; l.getElementsByTagName('head')[0].appendChild(r) })(window.document);
var app = (function () {
    'use strict';

    function noop() { }
    function add_location(element, file, line, column, char) {
        element.__svelte_meta = {
            loc: { file, line, column, char }
        };
    }
    function run(fn) {
        return fn();
    }
    function blank_object() {
        return Object.create(null);
    }
    function run_all(fns) {
        fns.forEach(run);
    }
    function is_function(thing) {
        return typeof thing === 'function';
    }
    function safe_not_equal(a, b) {
        return a != a ? b == b : a !== b || ((a && typeof a === 'object') || typeof a === 'function');
    }
    function is_empty(obj) {
        return Object.keys(obj).length === 0;
    }

    function append(target, node) {
        target.appendChild(node);
    }
    function insert(target, node, anchor) {
        target.insertBefore(node, anchor || null);
    }
    function detach(node) {
        node.parentNode.removeChild(node);
    }
    function destroy_each(iterations, detaching) {
        for (let i = 0; i < iterations.length; i += 1) {
            if (iterations[i])
                iterations[i].d(detaching);
        }
    }
    function element(name) {
        return document.createElement(name);
    }
    function text(data) {
        return document.createTextNode(data);
    }
    function space() {
        return text(' ');
    }
    function empty() {
        return text('');
    }
    function listen(node, event, handler, options) {
        node.addEventListener(event, handler, options);
        return () => node.removeEventListener(event, handler, options);
    }
    function attr(node, attribute, value) {
        if (value == null)
            node.removeAttribute(attribute);
        else if (node.getAttribute(attribute) !== value)
            node.setAttribute(attribute, value);
    }
    function children(element) {
        return Array.from(element.childNodes);
    }
    function set_input_value(input, value) {
        input.value = value == null ? '' : value;
    }
    function select_option(select, value) {
        for (let i = 0; i < select.options.length; i += 1) {
            const option = select.options[i];
            if (option.__value === value) {
                option.selected = true;
                return;
            }
        }
    }
    function select_value(select) {
        const selected_option = select.querySelector(':checked') || select.options[0];
        return selected_option && selected_option.__value;
    }
    function toggle_class(element, name, toggle) {
        element.classList[toggle ? 'add' : 'remove'](name);
    }
    function custom_event(type, detail) {
        const e = document.createEvent('CustomEvent');
        e.initCustomEvent(type, false, false, detail);
        return e;
    }

    let current_component;
    function set_current_component(component) {
        current_component = component;
    }
    function get_current_component() {
        if (!current_component)
            throw new Error(`Function called outside component initialization`);
        return current_component;
    }
    function onMount(fn) {
        get_current_component().$$.on_mount.push(fn);
    }
    function createEventDispatcher() {
        const component = get_current_component();
        return (type, detail) => {
            const callbacks = component.$$.callbacks[type];
            if (callbacks) {
                // TODO are there situations where events could be dispatched
                // in a server (non-DOM) environment?
                const event = custom_event(type, detail);
                callbacks.slice().forEach(fn => {
                    fn.call(component, event);
                });
            }
        };
    }

    const dirty_components = [];
    const binding_callbacks = [];
    const render_callbacks = [];
    const flush_callbacks = [];
    const resolved_promise = Promise.resolve();
    let update_scheduled = false;
    function schedule_update() {
        if (!update_scheduled) {
            update_scheduled = true;
            resolved_promise.then(flush);
        }
    }
    function add_render_callback(fn) {
        render_callbacks.push(fn);
    }
    function add_flush_callback(fn) {
        flush_callbacks.push(fn);
    }
    let flushing = false;
    const seen_callbacks = new Set();
    function flush() {
        if (flushing)
            return;
        flushing = true;
        do {
            // first, call beforeUpdate functions
            // and update components
            for (let i = 0; i < dirty_components.length; i += 1) {
                const component = dirty_components[i];
                set_current_component(component);
                update(component.$$);
            }
            dirty_components.length = 0;
            while (binding_callbacks.length)
                binding_callbacks.pop()();
            // then, once components are updated, call
            // afterUpdate functions. This may cause
            // subsequent updates...
            for (let i = 0; i < render_callbacks.length; i += 1) {
                const callback = render_callbacks[i];
                if (!seen_callbacks.has(callback)) {
                    // ...so guard against infinite loops
                    seen_callbacks.add(callback);
                    callback();
                }
            }
            render_callbacks.length = 0;
        } while (dirty_components.length);
        while (flush_callbacks.length) {
            flush_callbacks.pop()();
        }
        update_scheduled = false;
        flushing = false;
        seen_callbacks.clear();
    }
    function update($$) {
        if ($$.fragment !== null) {
            $$.update();
            run_all($$.before_update);
            const dirty = $$.dirty;
            $$.dirty = [-1];
            $$.fragment && $$.fragment.p($$.ctx, dirty);
            $$.after_update.forEach(add_render_callback);
        }
    }
    const outroing = new Set();
    let outros;
    function group_outros() {
        outros = {
            r: 0,
            c: [],
            p: outros // parent group
        };
    }
    function check_outros() {
        if (!outros.r) {
            run_all(outros.c);
        }
        outros = outros.p;
    }
    function transition_in(block, local) {
        if (block && block.i) {
            outroing.delete(block);
            block.i(local);
        }
    }
    function transition_out(block, local, detach, callback) {
        if (block && block.o) {
            if (outroing.has(block))
                return;
            outroing.add(block);
            outros.c.push(() => {
                outroing.delete(block);
                if (callback) {
                    if (detach)
                        block.d(1);
                    callback();
                }
            });
            block.o(local);
        }
    }

    const globals = (typeof window !== 'undefined'
        ? window
        : typeof globalThis !== 'undefined'
            ? globalThis
            : global);

    function bind(component, name, callback) {
        const index = component.$$.props[name];
        if (index !== undefined) {
            component.$$.bound[index] = callback;
            callback(component.$$.ctx[index]);
        }
    }
    function create_component(block) {
        block && block.c();
    }
    function mount_component(component, target, anchor) {
        const { fragment, on_mount, on_destroy, after_update } = component.$$;
        fragment && fragment.m(target, anchor);
        // onMount happens before the initial afterUpdate
        add_render_callback(() => {
            const new_on_destroy = on_mount.map(run).filter(is_function);
            if (on_destroy) {
                on_destroy.push(...new_on_destroy);
            }
            else {
                // Edge case - component was destroyed immediately,
                // most likely as a result of a binding initialising
                run_all(new_on_destroy);
            }
            component.$$.on_mount = [];
        });
        after_update.forEach(add_render_callback);
    }
    function destroy_component(component, detaching) {
        const $$ = component.$$;
        if ($$.fragment !== null) {
            run_all($$.on_destroy);
            $$.fragment && $$.fragment.d(detaching);
            // TODO null out other refs, including component.$$ (but need to
            // preserve final state?)
            $$.on_destroy = $$.fragment = null;
            $$.ctx = [];
        }
    }
    function make_dirty(component, i) {
        if (component.$$.dirty[0] === -1) {
            dirty_components.push(component);
            schedule_update();
            component.$$.dirty.fill(0);
        }
        component.$$.dirty[(i / 31) | 0] |= (1 << (i % 31));
    }
    function init(component, options, instance, create_fragment, not_equal, props, dirty = [-1]) {
        const parent_component = current_component;
        set_current_component(component);
        const prop_values = options.props || {};
        const $$ = component.$$ = {
            fragment: null,
            ctx: null,
            // state
            props,
            update: noop,
            not_equal,
            bound: blank_object(),
            // lifecycle
            on_mount: [],
            on_destroy: [],
            before_update: [],
            after_update: [],
            context: new Map(parent_component ? parent_component.$$.context : []),
            // everything else
            callbacks: blank_object(),
            dirty,
            skip_bound: false
        };
        let ready = false;
        $$.ctx = instance
            ? instance(component, prop_values, (i, ret, ...rest) => {
                const value = rest.length ? rest[0] : ret;
                if ($$.ctx && not_equal($$.ctx[i], $$.ctx[i] = value)) {
                    if (!$$.skip_bound && $$.bound[i])
                        $$.bound[i](value);
                    if (ready)
                        make_dirty(component, i);
                }
                return ret;
            })
            : [];
        $$.update();
        ready = true;
        run_all($$.before_update);
        // `false` as a special case of no DOM component
        $$.fragment = create_fragment ? create_fragment($$.ctx) : false;
        if (options.target) {
            if (options.hydrate) {
                const nodes = children(options.target);
                // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
                $$.fragment && $$.fragment.l(nodes);
                nodes.forEach(detach);
            }
            else {
                // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
                $$.fragment && $$.fragment.c();
            }
            if (options.intro)
                transition_in(component.$$.fragment);
            mount_component(component, options.target, options.anchor);
            flush();
        }
        set_current_component(parent_component);
    }
    class SvelteComponent {
        $destroy() {
            destroy_component(this, 1);
            this.$destroy = noop;
        }
        $on(type, callback) {
            const callbacks = (this.$$.callbacks[type] || (this.$$.callbacks[type] = []));
            callbacks.push(callback);
            return () => {
                const index = callbacks.indexOf(callback);
                if (index !== -1)
                    callbacks.splice(index, 1);
            };
        }
        $set($$props) {
            if (this.$$set && !is_empty($$props)) {
                this.$$.skip_bound = true;
                this.$$set($$props);
                this.$$.skip_bound = false;
            }
        }
    }

    function dispatch_dev(type, detail) {
        document.dispatchEvent(custom_event(type, Object.assign({ version: '3.24.1' }, detail)));
    }
    function append_dev(target, node) {
        dispatch_dev("SvelteDOMInsert", { target, node });
        append(target, node);
    }
    function insert_dev(target, node, anchor) {
        dispatch_dev("SvelteDOMInsert", { target, node, anchor });
        insert(target, node, anchor);
    }
    function detach_dev(node) {
        dispatch_dev("SvelteDOMRemove", { node });
        detach(node);
    }
    function listen_dev(node, event, handler, options, has_prevent_default, has_stop_propagation) {
        const modifiers = options === true ? ["capture"] : options ? Array.from(Object.keys(options)) : [];
        if (has_prevent_default)
            modifiers.push('preventDefault');
        if (has_stop_propagation)
            modifiers.push('stopPropagation');
        dispatch_dev("SvelteDOMAddEventListener", { node, event, handler, modifiers });
        const dispose = listen(node, event, handler, options);
        return () => {
            dispatch_dev("SvelteDOMRemoveEventListener", { node, event, handler, modifiers });
            dispose();
        };
    }
    function attr_dev(node, attribute, value) {
        attr(node, attribute, value);
        if (value == null)
            dispatch_dev("SvelteDOMRemoveAttribute", { node, attribute });
        else
            dispatch_dev("SvelteDOMSetAttribute", { node, attribute, value });
    }
    function prop_dev(node, property, value) {
        node[property] = value;
        dispatch_dev("SvelteDOMSetProperty", { node, property, value });
    }
    function set_data_dev(text, data) {
        data = '' + data;
        if (text.wholeText === data)
            return;
        dispatch_dev("SvelteDOMSetData", { node: text, data });
        text.data = data;
    }
    function validate_each_argument(arg) {
        if (typeof arg !== 'string' && !(arg && typeof arg === 'object' && 'length' in arg)) {
            let msg = '{#each} only iterates over array-like objects.';
            if (typeof Symbol === 'function' && arg && Symbol.iterator in arg) {
                msg += ' You can use a spread to convert this iterable into an array.';
            }
            throw new Error(msg);
        }
    }
    function validate_slots(name, slot, keys) {
        for (const slot_key of Object.keys(slot)) {
            if (!~keys.indexOf(slot_key)) {
                console.warn(`<${name}> received an unexpected slot "${slot_key}".`);
            }
        }
    }
    class SvelteComponentDev extends SvelteComponent {
        constructor(options) {
            if (!options || (!options.target && !options.$$inline)) {
                throw new Error(`'target' is a required option`);
            }
            super();
        }
        $destroy() {
            super.$destroy();
            this.$destroy = () => {
                console.warn(`Component was already destroyed`); // eslint-disable-line no-console
            };
        }
        $capture_state() { }
        $inject_state() { }
    }

    // Current version.
    var VERSION = '1.11.0';

    // Establish the root object, `window` (`self`) in the browser, `global`
    // on the server, or `this` in some virtual machines. We use `self`
    // instead of `window` for `WebWorker` support.
    var root = typeof self == 'object' && self.self === self && self ||
              typeof global == 'object' && global.global === global && global ||
              Function('return this')() ||
              {};

    // Save bytes in the minified (but not gzipped) version:
    var ArrayProto = Array.prototype, ObjProto = Object.prototype;
    var SymbolProto = typeof Symbol !== 'undefined' ? Symbol.prototype : null;

    // Create quick reference variables for speed access to core prototypes.
    var push = ArrayProto.push,
        slice = ArrayProto.slice,
        toString = ObjProto.toString,
        hasOwnProperty = ObjProto.hasOwnProperty;

    // Modern feature detection.
    var supportsArrayBuffer = typeof ArrayBuffer !== 'undefined';

    // All **ECMAScript 5+** native function implementations that we hope to use
    // are declared here.
    var nativeIsArray = Array.isArray,
        nativeKeys = Object.keys,
        nativeCreate = Object.create,
        nativeIsView = supportsArrayBuffer && ArrayBuffer.isView;

    // Create references to these builtin functions because we override them.
    var _isNaN = isNaN,
        _isFinite = isFinite;

    // Keys in IE < 9 that won't be iterated by `for key in ...` and thus missed.
    var hasEnumBug = !{toString: null}.propertyIsEnumerable('toString');
    var nonEnumerableProps = ['valueOf', 'isPrototypeOf', 'toString',
      'propertyIsEnumerable', 'hasOwnProperty', 'toLocaleString'];

    // The largest integer that can be represented exactly.
    var MAX_ARRAY_INDEX = Math.pow(2, 53) - 1;

    // Some functions take a variable number of arguments, or a few expected
    // arguments at the beginning and then a variable number of values to operate
    // on. This helper accumulates all remaining arguments past the function’s
    // argument length (or an explicit `startIndex`), into an array that becomes
    // the last argument. Similar to ES6’s "rest parameter".
    function restArguments(func, startIndex) {
      startIndex = startIndex == null ? func.length - 1 : +startIndex;
      return function() {
        var length = Math.max(arguments.length - startIndex, 0),
            rest = Array(length),
            index = 0;
        for (; index < length; index++) {
          rest[index] = arguments[index + startIndex];
        }
        switch (startIndex) {
          case 0: return func.call(this, rest);
          case 1: return func.call(this, arguments[0], rest);
          case 2: return func.call(this, arguments[0], arguments[1], rest);
        }
        var args = Array(startIndex + 1);
        for (index = 0; index < startIndex; index++) {
          args[index] = arguments[index];
        }
        args[startIndex] = rest;
        return func.apply(this, args);
      };
    }

    // Is a given variable an object?
    function isObject(obj) {
      var type = typeof obj;
      return type === 'function' || type === 'object' && !!obj;
    }

    // Is a given value equal to null?
    function isNull(obj) {
      return obj === null;
    }

    // Is a given variable undefined?
    function isUndefined(obj) {
      return obj === void 0;
    }

    // Is a given value a boolean?
    function isBoolean(obj) {
      return obj === true || obj === false || toString.call(obj) === '[object Boolean]';
    }

    // Is a given value a DOM element?
    function isElement(obj) {
      return !!(obj && obj.nodeType === 1);
    }

    // Internal function for creating a `toString`-based type tester.
    function tagTester(name) {
      return function(obj) {
        return toString.call(obj) === '[object ' + name + ']';
      };
    }

    var isString = tagTester('String');

    var isNumber = tagTester('Number');

    var isDate = tagTester('Date');

    var isRegExp = tagTester('RegExp');

    var isError = tagTester('Error');

    var isSymbol = tagTester('Symbol');

    var isMap = tagTester('Map');

    var isWeakMap = tagTester('WeakMap');

    var isSet = tagTester('Set');

    var isWeakSet = tagTester('WeakSet');

    var isArrayBuffer = tagTester('ArrayBuffer');

    var isDataView = tagTester('DataView');

    // Is a given value an array?
    // Delegates to ECMA5's native `Array.isArray`.
    var isArray = nativeIsArray || tagTester('Array');

    var isFunction = tagTester('Function');

    // Optimize `isFunction` if appropriate. Work around some `typeof` bugs in old
    // v8, IE 11 (#1621), Safari 8 (#1929), and PhantomJS (#2236).
    var nodelist = root.document && root.document.childNodes;
    if (typeof /./ != 'function' && typeof Int8Array != 'object' && typeof nodelist != 'function') {
      isFunction = function(obj) {
        return typeof obj == 'function' || false;
      };
    }

    var isFunction$1 = isFunction;

    // Internal function to check whether `key` is an own property name of `obj`.
    function has(obj, key) {
      return obj != null && hasOwnProperty.call(obj, key);
    }

    var isArguments = tagTester('Arguments');

    // Define a fallback version of the method in browsers (ahem, IE < 9), where
    // there isn't any inspectable "Arguments" type.
    (function() {
      if (!isArguments(arguments)) {
        isArguments = function(obj) {
          return has(obj, 'callee');
        };
      }
    }());

    var isArguments$1 = isArguments;

    // Is a given object a finite number?
    function isFinite$1(obj) {
      return !isSymbol(obj) && _isFinite(obj) && !isNaN(parseFloat(obj));
    }

    // Is the given value `NaN`?
    function isNaN$1(obj) {
      return isNumber(obj) && _isNaN(obj);
    }

    // Predicate-generating function. Often useful outside of Underscore.
    function constant(value) {
      return function() {
        return value;
      };
    }

    // Common internal logic for `isArrayLike` and `isBufferLike`.
    function createSizePropertyCheck(getSizeProperty) {
      return function(collection) {
        var sizeProperty = getSizeProperty(collection);
        return typeof sizeProperty == 'number' && sizeProperty >= 0 && sizeProperty <= MAX_ARRAY_INDEX;
      }
    }

    // Internal helper to generate a function to obtain property `key` from `obj`.
    function shallowProperty(key) {
      return function(obj) {
        return obj == null ? void 0 : obj[key];
      };
    }

    // Internal helper to obtain the `byteLength` property of an object.
    var getByteLength = shallowProperty('byteLength');

    // Internal helper to determine whether we should spend extensive checks against
    // `ArrayBuffer` et al.
    var isBufferLike = createSizePropertyCheck(getByteLength);

    // Is a given value a typed array?
    var typedArrayPattern = /\[object ((I|Ui)nt(8|16|32)|Float(32|64)|Uint8Clamped|Big(I|Ui)nt64)Array\]/;
    function isTypedArray(obj) {
      // `ArrayBuffer.isView` is the most future-proof, so use it when available.
      // Otherwise, fall back on the above regular expression.
      return nativeIsView ? (nativeIsView(obj) && !isDataView(obj)) :
                    isBufferLike(obj) && typedArrayPattern.test(toString.call(obj));
    }

    var isTypedArray$1 = supportsArrayBuffer ? isTypedArray : constant(false);

    // Internal helper to obtain the `length` property of an object.
    var getLength = shallowProperty('length');

    // Internal helper for collection methods to determine whether a collection
    // should be iterated as an array or as an object.
    // Related: https://people.mozilla.org/~jorendorff/es6-draft.html#sec-tolength
    // Avoids a very nasty iOS 8 JIT bug on ARM-64. #2094
    var isArrayLike = createSizePropertyCheck(getLength);

    // Internal helper to create a simple lookup structure.
    // `collectNonEnumProps` used to depend on `_.contains`, but this led to
    // circular imports. `emulatedSet` is a one-off solution that only works for
    // arrays of strings.
    function emulatedSet(keys) {
      var hash = {};
      for (var l = keys.length, i = 0; i < l; ++i) hash[keys[i]] = true;
      return {
        contains: function(key) { return hash[key]; },
        push: function(key) {
          hash[key] = true;
          return keys.push(key);
        }
      };
    }

    // Internal helper. Checks `keys` for the presence of keys in IE < 9 that won't
    // be iterated by `for key in ...` and thus missed. Extends `keys` in place if
    // needed.
    function collectNonEnumProps(obj, keys) {
      keys = emulatedSet(keys);
      var nonEnumIdx = nonEnumerableProps.length;
      var constructor = obj.constructor;
      var proto = isFunction$1(constructor) && constructor.prototype || ObjProto;

      // Constructor is a special case.
      var prop = 'constructor';
      if (has(obj, prop) && !keys.contains(prop)) keys.push(prop);

      while (nonEnumIdx--) {
        prop = nonEnumerableProps[nonEnumIdx];
        if (prop in obj && obj[prop] !== proto[prop] && !keys.contains(prop)) {
          keys.push(prop);
        }
      }
    }

    // Retrieve the names of an object's own properties.
    // Delegates to **ECMAScript 5**'s native `Object.keys`.
    function keys(obj) {
      if (!isObject(obj)) return [];
      if (nativeKeys) return nativeKeys(obj);
      var keys = [];
      for (var key in obj) if (has(obj, key)) keys.push(key);
      // Ahem, IE < 9.
      if (hasEnumBug) collectNonEnumProps(obj, keys);
      return keys;
    }

    // Is a given array, string, or object empty?
    // An "empty" object has no enumerable own-properties.
    function isEmpty(obj) {
      if (obj == null) return true;
      // Skip the more expensive `toString`-based type checks if `obj` has no
      // `.length`.
      if (isArrayLike(obj) && (isArray(obj) || isString(obj) || isArguments$1(obj))) return obj.length === 0;
      return keys(obj).length === 0;
    }

    // Returns whether an object has a given set of `key:value` pairs.
    function isMatch(object, attrs) {
      var _keys = keys(attrs), length = _keys.length;
      if (object == null) return !length;
      var obj = Object(object);
      for (var i = 0; i < length; i++) {
        var key = _keys[i];
        if (attrs[key] !== obj[key] || !(key in obj)) return false;
      }
      return true;
    }

    // If Underscore is called as a function, it returns a wrapped object that can
    // be used OO-style. This wrapper holds altered versions of all functions added
    // through `_.mixin`. Wrapped objects may be chained.
    function _(obj) {
      if (obj instanceof _) return obj;
      if (!(this instanceof _)) return new _(obj);
      this._wrapped = obj;
    }

    _.VERSION = VERSION;

    // Extracts the result from a wrapped and chained object.
    _.prototype.value = function() {
      return this._wrapped;
    };

    // Provide unwrapping proxies for some methods used in engine operations
    // such as arithmetic and JSON stringification.
    _.prototype.valueOf = _.prototype.toJSON = _.prototype.value;

    _.prototype.toString = function() {
      return String(this._wrapped);
    };

    // Internal recursive comparison function for `_.isEqual`.
    function eq(a, b, aStack, bStack) {
      // Identical objects are equal. `0 === -0`, but they aren't identical.
      // See the [Harmony `egal` proposal](https://wiki.ecmascript.org/doku.php?id=harmony:egal).
      if (a === b) return a !== 0 || 1 / a === 1 / b;
      // `null` or `undefined` only equal to itself (strict comparison).
      if (a == null || b == null) return false;
      // `NaN`s are equivalent, but non-reflexive.
      if (a !== a) return b !== b;
      // Exhaust primitive checks
      var type = typeof a;
      if (type !== 'function' && type !== 'object' && typeof b != 'object') return false;
      return deepEq(a, b, aStack, bStack);
    }

    // Internal recursive comparison function for `_.isEqual`.
    function deepEq(a, b, aStack, bStack) {
      // Unwrap any wrapped objects.
      if (a instanceof _) a = a._wrapped;
      if (b instanceof _) b = b._wrapped;
      // Compare `[[Class]]` names.
      var className = toString.call(a);
      if (className !== toString.call(b)) return false;
      switch (className) {
        // These types are compared by value.
        case '[object RegExp]':
          // RegExps are coerced to strings for comparison (Note: '' + /a/i === '/a/i')
        case '[object String]':
          // Primitives and their corresponding object wrappers are equivalent; thus, `"5"` is
          // equivalent to `new String("5")`.
          return '' + a === '' + b;
        case '[object Number]':
          // `NaN`s are equivalent, but non-reflexive.
          // Object(NaN) is equivalent to NaN.
          if (+a !== +a) return +b !== +b;
          // An `egal` comparison is performed for other numeric values.
          return +a === 0 ? 1 / +a === 1 / b : +a === +b;
        case '[object Date]':
        case '[object Boolean]':
          // Coerce dates and booleans to numeric primitive values. Dates are compared by their
          // millisecond representations. Note that invalid dates with millisecond representations
          // of `NaN` are not equivalent.
          return +a === +b;
        case '[object Symbol]':
          return SymbolProto.valueOf.call(a) === SymbolProto.valueOf.call(b);
        case '[object ArrayBuffer]':
          // Coerce to `DataView` so we can fall through to the next case.
          return deepEq(new DataView(a), new DataView(b), aStack, bStack);
        case '[object DataView]':
          var byteLength = getByteLength(a);
          if (byteLength !== getByteLength(b)) {
            return false;
          }
          while (byteLength--) {
            if (a.getUint8(byteLength) !== b.getUint8(byteLength)) {
              return false;
            }
          }
          return true;
      }

      if (isTypedArray$1(a)) {
        // Coerce typed arrays to `DataView`.
        return deepEq(new DataView(a.buffer), new DataView(b.buffer), aStack, bStack);
      }

      var areArrays = className === '[object Array]';
      if (!areArrays) {
        if (typeof a != 'object' || typeof b != 'object') return false;

        // Objects with different constructors are not equivalent, but `Object`s or `Array`s
        // from different frames are.
        var aCtor = a.constructor, bCtor = b.constructor;
        if (aCtor !== bCtor && !(isFunction$1(aCtor) && aCtor instanceof aCtor &&
                                 isFunction$1(bCtor) && bCtor instanceof bCtor)
                            && ('constructor' in a && 'constructor' in b)) {
          return false;
        }
      }
      // Assume equality for cyclic structures. The algorithm for detecting cyclic
      // structures is adapted from ES 5.1 section 15.12.3, abstract operation `JO`.

      // Initializing stack of traversed objects.
      // It's done here since we only need them for objects and arrays comparison.
      aStack = aStack || [];
      bStack = bStack || [];
      var length = aStack.length;
      while (length--) {
        // Linear search. Performance is inversely proportional to the number of
        // unique nested structures.
        if (aStack[length] === a) return bStack[length] === b;
      }

      // Add the first object to the stack of traversed objects.
      aStack.push(a);
      bStack.push(b);

      // Recursively compare objects and arrays.
      if (areArrays) {
        // Compare array lengths to determine if a deep comparison is necessary.
        length = a.length;
        if (length !== b.length) return false;
        // Deep compare the contents, ignoring non-numeric properties.
        while (length--) {
          if (!eq(a[length], b[length], aStack, bStack)) return false;
        }
      } else {
        // Deep compare objects.
        var _keys = keys(a), key;
        length = _keys.length;
        // Ensure that both objects contain the same number of properties before comparing deep equality.
        if (keys(b).length !== length) return false;
        while (length--) {
          // Deep compare each member
          key = _keys[length];
          if (!(has(b, key) && eq(a[key], b[key], aStack, bStack))) return false;
        }
      }
      // Remove the first object from the stack of traversed objects.
      aStack.pop();
      bStack.pop();
      return true;
    }

    // Perform a deep comparison to check if two objects are equal.
    function isEqual(a, b) {
      return eq(a, b);
    }

    // Retrieve all the enumerable property names of an object.
    function allKeys(obj) {
      if (!isObject(obj)) return [];
      var keys = [];
      for (var key in obj) keys.push(key);
      // Ahem, IE < 9.
      if (hasEnumBug) collectNonEnumProps(obj, keys);
      return keys;
    }

    // Retrieve the values of an object's properties.
    function values(obj) {
      var _keys = keys(obj);
      var length = _keys.length;
      var values = Array(length);
      for (var i = 0; i < length; i++) {
        values[i] = obj[_keys[i]];
      }
      return values;
    }

    // Convert an object into a list of `[key, value]` pairs.
    // The opposite of `_.object` with one argument.
    function pairs(obj) {
      var _keys = keys(obj);
      var length = _keys.length;
      var pairs = Array(length);
      for (var i = 0; i < length; i++) {
        pairs[i] = [_keys[i], obj[_keys[i]]];
      }
      return pairs;
    }

    // Invert the keys and values of an object. The values must be serializable.
    function invert(obj) {
      var result = {};
      var _keys = keys(obj);
      for (var i = 0, length = _keys.length; i < length; i++) {
        result[obj[_keys[i]]] = _keys[i];
      }
      return result;
    }

    // Return a sorted list of the function names available on the object.
    function functions(obj) {
      var names = [];
      for (var key in obj) {
        if (isFunction$1(obj[key])) names.push(key);
      }
      return names.sort();
    }

    // An internal function for creating assigner functions.
    function createAssigner(keysFunc, defaults) {
      return function(obj) {
        var length = arguments.length;
        if (defaults) obj = Object(obj);
        if (length < 2 || obj == null) return obj;
        for (var index = 1; index < length; index++) {
          var source = arguments[index],
              keys = keysFunc(source),
              l = keys.length;
          for (var i = 0; i < l; i++) {
            var key = keys[i];
            if (!defaults || obj[key] === void 0) obj[key] = source[key];
          }
        }
        return obj;
      };
    }

    // Extend a given object with all the properties in passed-in object(s).
    var extend = createAssigner(allKeys);

    // Assigns a given object with all the own properties in the passed-in
    // object(s).
    // (https://developer.mozilla.org/docs/Web/JavaScript/Reference/Global_Objects/Object/assign)
    var extendOwn = createAssigner(keys);

    // Fill in a given object with default properties.
    var defaults = createAssigner(allKeys, true);

    // Create a naked function reference for surrogate-prototype-swapping.
    function ctor() {
      return function(){};
    }

    // An internal function for creating a new object that inherits from another.
    function baseCreate(prototype) {
      if (!isObject(prototype)) return {};
      if (nativeCreate) return nativeCreate(prototype);
      var Ctor = ctor();
      Ctor.prototype = prototype;
      var result = new Ctor;
      Ctor.prototype = null;
      return result;
    }

    // Creates an object that inherits from the given prototype object.
    // If additional properties are provided then they will be added to the
    // created object.
    function create(prototype, props) {
      var result = baseCreate(prototype);
      if (props) extendOwn(result, props);
      return result;
    }

    // Create a (shallow-cloned) duplicate of an object.
    function clone(obj) {
      if (!isObject(obj)) return obj;
      return isArray(obj) ? obj.slice() : extend({}, obj);
    }

    // Invokes `interceptor` with the `obj` and then returns `obj`.
    // The primary purpose of this method is to "tap into" a method chain, in
    // order to perform operations on intermediate results within the chain.
    function tap(obj, interceptor) {
      interceptor(obj);
      return obj;
    }

    // Shortcut function for checking if an object has a given property directly on
    // itself (in other words, not on a prototype). Unlike the internal `has`
    // function, this public version can also traverse nested properties.
    function has$1(obj, path) {
      if (!isArray(path)) {
        return has(obj, path);
      }
      var length = path.length;
      for (var i = 0; i < length; i++) {
        var key = path[i];
        if (obj == null || !hasOwnProperty.call(obj, key)) {
          return false;
        }
        obj = obj[key];
      }
      return !!length;
    }

    // Keep the identity function around for default iteratees.
    function identity(value) {
      return value;
    }

    // Returns a predicate for checking whether an object has a given set of
    // `key:value` pairs.
    function matcher(attrs) {
      attrs = extendOwn({}, attrs);
      return function(obj) {
        return isMatch(obj, attrs);
      };
    }

    // Internal function to obtain a nested property in `obj` along `path`.
    function deepGet(obj, path) {
      var length = path.length;
      for (var i = 0; i < length; i++) {
        if (obj == null) return void 0;
        obj = obj[path[i]];
      }
      return length ? obj : void 0;
    }

    // Creates a function that, when passed an object, will traverse that object’s
    // properties down the given `path`, specified as an array of keys or indices.
    function property(path) {
      if (!isArray(path)) {
        return shallowProperty(path);
      }
      return function(obj) {
        return deepGet(obj, path);
      };
    }

    // Internal function that returns an efficient (for current engines) version
    // of the passed-in callback, to be repeatedly applied in other Underscore
    // functions.
    function optimizeCb(func, context, argCount) {
      if (context === void 0) return func;
      switch (argCount == null ? 3 : argCount) {
        case 1: return function(value) {
          return func.call(context, value);
        };
        // The 2-argument case is omitted because we’re not using it.
        case 3: return function(value, index, collection) {
          return func.call(context, value, index, collection);
        };
        case 4: return function(accumulator, value, index, collection) {
          return func.call(context, accumulator, value, index, collection);
        };
      }
      return function() {
        return func.apply(context, arguments);
      };
    }

    // An internal function to generate callbacks that can be applied to each
    // element in a collection, returning the desired result — either `_.identity`,
    // an arbitrary callback, a property matcher, or a property accessor.
    function baseIteratee(value, context, argCount) {
      if (value == null) return identity;
      if (isFunction$1(value)) return optimizeCb(value, context, argCount);
      if (isObject(value) && !isArray(value)) return matcher(value);
      return property(value);
    }

    // External wrapper for our callback generator. Users may customize
    // `_.iteratee` if they want additional predicate/iteratee shorthand styles.
    // This abstraction hides the internal-only `argCount` argument.
    function iteratee(value, context) {
      return baseIteratee(value, context, Infinity);
    }
    _.iteratee = iteratee;

    // The function we call internally to generate a callback. It invokes
    // `_.iteratee` if overridden, otherwise `baseIteratee`.
    function cb(value, context, argCount) {
      if (_.iteratee !== iteratee) return _.iteratee(value, context);
      return baseIteratee(value, context, argCount);
    }

    // Returns the results of applying the `iteratee` to each element of `obj`.
    // In contrast to `_.map` it returns an object.
    function mapObject(obj, iteratee, context) {
      iteratee = cb(iteratee, context);
      var _keys = keys(obj),
          length = _keys.length,
          results = {};
      for (var index = 0; index < length; index++) {
        var currentKey = _keys[index];
        results[currentKey] = iteratee(obj[currentKey], currentKey, obj);
      }
      return results;
    }

    // Predicate-generating function. Often useful outside of Underscore.
    function noop$1(){}

    // Generates a function for a given object that returns a given property.
    function propertyOf(obj) {
      if (obj == null) {
        return function(){};
      }
      return function(path) {
        return !isArray(path) ? obj[path] : deepGet(obj, path);
      };
    }

    // Run a function **n** times.
    function times(n, iteratee, context) {
      var accum = Array(Math.max(0, n));
      iteratee = optimizeCb(iteratee, context, 1);
      for (var i = 0; i < n; i++) accum[i] = iteratee(i);
      return accum;
    }

    // Return a random integer between `min` and `max` (inclusive).
    function random(min, max) {
      if (max == null) {
        max = min;
        min = 0;
      }
      return min + Math.floor(Math.random() * (max - min + 1));
    }

    // A (possibly faster) way to get the current timestamp as an integer.
    var now = Date.now || function() {
      return new Date().getTime();
    };

    // Internal helper to generate functions for escaping and unescaping strings
    // to/from HTML interpolation.
    function createEscaper(map) {
      var escaper = function(match) {
        return map[match];
      };
      // Regexes for identifying a key that needs to be escaped.
      var source = '(?:' + keys(map).join('|') + ')';
      var testRegexp = RegExp(source);
      var replaceRegexp = RegExp(source, 'g');
      return function(string) {
        string = string == null ? '' : '' + string;
        return testRegexp.test(string) ? string.replace(replaceRegexp, escaper) : string;
      };
    }

    // Internal list of HTML entities for escaping.
    var escapeMap = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#x27;',
      '`': '&#x60;'
    };

    // Function for escaping strings to HTML interpolation.
    var _escape = createEscaper(escapeMap);

    // Internal list of HTML entities for unescaping.
    var unescapeMap = invert(escapeMap);

    // Function for unescaping strings from HTML interpolation.
    var _unescape = createEscaper(unescapeMap);

    // By default, Underscore uses ERB-style template delimiters. Change the
    // following template settings to use alternative delimiters.
    var templateSettings = _.templateSettings = {
      evaluate: /<%([\s\S]+?)%>/g,
      interpolate: /<%=([\s\S]+?)%>/g,
      escape: /<%-([\s\S]+?)%>/g
    };

    // When customizing `_.templateSettings`, if you don't want to define an
    // interpolation, evaluation or escaping regex, we need one that is
    // guaranteed not to match.
    var noMatch = /(.)^/;

    // Certain characters need to be escaped so that they can be put into a
    // string literal.
    var escapes = {
      "'": "'",
      '\\': '\\',
      '\r': 'r',
      '\n': 'n',
      '\u2028': 'u2028',
      '\u2029': 'u2029'
    };

    var escapeRegExp = /\\|'|\r|\n|\u2028|\u2029/g;

    function escapeChar(match) {
      return '\\' + escapes[match];
    }

    // JavaScript micro-templating, similar to John Resig's implementation.
    // Underscore templating handles arbitrary delimiters, preserves whitespace,
    // and correctly escapes quotes within interpolated code.
    // NB: `oldSettings` only exists for backwards compatibility.
    function template(text, settings, oldSettings) {
      if (!settings && oldSettings) settings = oldSettings;
      settings = defaults({}, settings, _.templateSettings);

      // Combine delimiters into one regular expression via alternation.
      var matcher = RegExp([
        (settings.escape || noMatch).source,
        (settings.interpolate || noMatch).source,
        (settings.evaluate || noMatch).source
      ].join('|') + '|$', 'g');

      // Compile the template source, escaping string literals appropriately.
      var index = 0;
      var source = "__p+='";
      text.replace(matcher, function(match, escape, interpolate, evaluate, offset) {
        source += text.slice(index, offset).replace(escapeRegExp, escapeChar);
        index = offset + match.length;

        if (escape) {
          source += "'+\n((__t=(" + escape + "))==null?'':_.escape(__t))+\n'";
        } else if (interpolate) {
          source += "'+\n((__t=(" + interpolate + "))==null?'':__t)+\n'";
        } else if (evaluate) {
          source += "';\n" + evaluate + "\n__p+='";
        }

        // Adobe VMs need the match returned to produce the correct offset.
        return match;
      });
      source += "';\n";

      // If a variable is not specified, place data values in local scope.
      if (!settings.variable) source = 'with(obj||{}){\n' + source + '}\n';

      source = "var __t,__p='',__j=Array.prototype.join," +
        "print=function(){__p+=__j.call(arguments,'');};\n" +
        source + 'return __p;\n';

      var render;
      try {
        render = new Function(settings.variable || 'obj', '_', source);
      } catch (e) {
        e.source = source;
        throw e;
      }

      var template = function(data) {
        return render.call(this, data, _);
      };

      // Provide the compiled source as a convenience for precompilation.
      var argument = settings.variable || 'obj';
      template.source = 'function(' + argument + '){\n' + source + '}';

      return template;
    }

    // Traverses the children of `obj` along `path`. If a child is a function, it
    // is invoked with its parent as context. Returns the value of the final
    // child, or `fallback` if any child is undefined.
    function result(obj, path, fallback) {
      if (!isArray(path)) path = [path];
      var length = path.length;
      if (!length) {
        return isFunction$1(fallback) ? fallback.call(obj) : fallback;
      }
      for (var i = 0; i < length; i++) {
        var prop = obj == null ? void 0 : obj[path[i]];
        if (prop === void 0) {
          prop = fallback;
          i = length; // Ensure we don't continue iterating.
        }
        obj = isFunction$1(prop) ? prop.call(obj) : prop;
      }
      return obj;
    }

    // Generate a unique integer id (unique within the entire client session).
    // Useful for temporary DOM ids.
    var idCounter = 0;
    function uniqueId(prefix) {
      var id = ++idCounter + '';
      return prefix ? prefix + id : id;
    }

    // Start chaining a wrapped Underscore object.
    function chain(obj) {
      var instance = _(obj);
      instance._chain = true;
      return instance;
    }

    // Internal function to execute `sourceFunc` bound to `context` with optional
    // `args`. Determines whether to execute a function as a constructor or as a
    // normal function.
    function executeBound(sourceFunc, boundFunc, context, callingContext, args) {
      if (!(callingContext instanceof boundFunc)) return sourceFunc.apply(context, args);
      var self = baseCreate(sourceFunc.prototype);
      var result = sourceFunc.apply(self, args);
      if (isObject(result)) return result;
      return self;
    }

    // Partially apply a function by creating a version that has had some of its
    // arguments pre-filled, without changing its dynamic `this` context. `_` acts
    // as a placeholder by default, allowing any combination of arguments to be
    // pre-filled. Set `_.partial.placeholder` for a custom placeholder argument.
    var partial = restArguments(function(func, boundArgs) {
      var placeholder = partial.placeholder;
      var bound = function() {
        var position = 0, length = boundArgs.length;
        var args = Array(length);
        for (var i = 0; i < length; i++) {
          args[i] = boundArgs[i] === placeholder ? arguments[position++] : boundArgs[i];
        }
        while (position < arguments.length) args.push(arguments[position++]);
        return executeBound(func, bound, this, this, args);
      };
      return bound;
    });

    partial.placeholder = _;

    // Create a function bound to a given object (assigning `this`, and arguments,
    // optionally).
    var bind$1 = restArguments(function(func, context, args) {
      if (!isFunction$1(func)) throw new TypeError('Bind must be called on a function');
      var bound = restArguments(function(callArgs) {
        return executeBound(func, bound, context, this, args.concat(callArgs));
      });
      return bound;
    });

    // Internal implementation of a recursive `flatten` function.
    function flatten(input, depth, strict, output) {
      output = output || [];
      if (!depth && depth !== 0) {
        depth = Infinity;
      } else if (depth <= 0) {
        return output.concat(input);
      }
      var idx = output.length;
      for (var i = 0, length = getLength(input); i < length; i++) {
        var value = input[i];
        if (isArrayLike(value) && (isArray(value) || isArguments$1(value))) {
          // Flatten current level of array or arguments object.
          if (depth > 1) {
            flatten(value, depth - 1, strict, output);
            idx = output.length;
          } else {
            var j = 0, len = value.length;
            while (j < len) output[idx++] = value[j++];
          }
        } else if (!strict) {
          output[idx++] = value;
        }
      }
      return output;
    }

    // Bind a number of an object's methods to that object. Remaining arguments
    // are the method names to be bound. Useful for ensuring that all callbacks
    // defined on an object belong to it.
    var bindAll = restArguments(function(obj, keys) {
      keys = flatten(keys, false, false);
      var index = keys.length;
      if (index < 1) throw new Error('bindAll must be passed function names');
      while (index--) {
        var key = keys[index];
        obj[key] = bind$1(obj[key], obj);
      }
      return obj;
    });

    // Memoize an expensive function by storing its results.
    function memoize(func, hasher) {
      var memoize = function(key) {
        var cache = memoize.cache;
        var address = '' + (hasher ? hasher.apply(this, arguments) : key);
        if (!has(cache, address)) cache[address] = func.apply(this, arguments);
        return cache[address];
      };
      memoize.cache = {};
      return memoize;
    }

    // Delays a function for the given number of milliseconds, and then calls
    // it with the arguments supplied.
    var delay = restArguments(function(func, wait, args) {
      return setTimeout(function() {
        return func.apply(null, args);
      }, wait);
    });

    // Defers a function, scheduling it to run after the current call stack has
    // cleared.
    var defer = partial(delay, _, 1);

    // Returns a function, that, when invoked, will only be triggered at most once
    // during a given window of time. Normally, the throttled function will run
    // as much as it can, without ever going more than once per `wait` duration;
    // but if you'd like to disable the execution on the leading edge, pass
    // `{leading: false}`. To disable execution on the trailing edge, ditto.
    function throttle(func, wait, options) {
      var timeout, context, args, result;
      var previous = 0;
      if (!options) options = {};

      var later = function() {
        previous = options.leading === false ? 0 : now();
        timeout = null;
        result = func.apply(context, args);
        if (!timeout) context = args = null;
      };

      var throttled = function() {
        var _now = now();
        if (!previous && options.leading === false) previous = _now;
        var remaining = wait - (_now - previous);
        context = this;
        args = arguments;
        if (remaining <= 0 || remaining > wait) {
          if (timeout) {
            clearTimeout(timeout);
            timeout = null;
          }
          previous = _now;
          result = func.apply(context, args);
          if (!timeout) context = args = null;
        } else if (!timeout && options.trailing !== false) {
          timeout = setTimeout(later, remaining);
        }
        return result;
      };

      throttled.cancel = function() {
        clearTimeout(timeout);
        previous = 0;
        timeout = context = args = null;
      };

      return throttled;
    }

    // When a sequence of calls of the returned function ends, the argument
    // function is triggered. The end of a sequence is defined by the `wait`
    // parameter. If `immediate` is passed, the argument function will be
    // triggered at the beginning of the sequence instead of at the end.
    function debounce(func, wait, immediate) {
      var timeout, result;

      var later = function(context, args) {
        timeout = null;
        if (args) result = func.apply(context, args);
      };

      var debounced = restArguments(function(args) {
        if (timeout) clearTimeout(timeout);
        if (immediate) {
          var callNow = !timeout;
          timeout = setTimeout(later, wait);
          if (callNow) result = func.apply(this, args);
        } else {
          timeout = delay(later, wait, this, args);
        }

        return result;
      });

      debounced.cancel = function() {
        clearTimeout(timeout);
        timeout = null;
      };

      return debounced;
    }

    // Returns the first function passed as an argument to the second,
    // allowing you to adjust arguments, run code before and after, and
    // conditionally execute the original function.
    function wrap(func, wrapper) {
      return partial(wrapper, func);
    }

    // Returns a negated version of the passed-in predicate.
    function negate(predicate) {
      return function() {
        return !predicate.apply(this, arguments);
      };
    }

    // Returns a function that is the composition of a list of functions, each
    // consuming the return value of the function that follows.
    function compose() {
      var args = arguments;
      var start = args.length - 1;
      return function() {
        var i = start;
        var result = args[start].apply(this, arguments);
        while (i--) result = args[i].call(this, result);
        return result;
      };
    }

    // Returns a function that will only be executed on and after the Nth call.
    function after(times, func) {
      return function() {
        if (--times < 1) {
          return func.apply(this, arguments);
        }
      };
    }

    // Returns a function that will only be executed up to (but not including) the
    // Nth call.
    function before(times, func) {
      var memo;
      return function() {
        if (--times > 0) {
          memo = func.apply(this, arguments);
        }
        if (times <= 1) func = null;
        return memo;
      };
    }

    // Returns a function that will be executed at most one time, no matter how
    // often you call it. Useful for lazy initialization.
    var once = partial(before, 2);

    // Returns the first key on an object that passes a truth test.
    function findKey(obj, predicate, context) {
      predicate = cb(predicate, context);
      var _keys = keys(obj), key;
      for (var i = 0, length = _keys.length; i < length; i++) {
        key = _keys[i];
        if (predicate(obj[key], key, obj)) return key;
      }
    }

    // Internal function to generate `_.findIndex` and `_.findLastIndex`.
    function createPredicateIndexFinder(dir) {
      return function(array, predicate, context) {
        predicate = cb(predicate, context);
        var length = getLength(array);
        var index = dir > 0 ? 0 : length - 1;
        for (; index >= 0 && index < length; index += dir) {
          if (predicate(array[index], index, array)) return index;
        }
        return -1;
      };
    }

    // Returns the first index on an array-like that passes a truth test.
    var findIndex = createPredicateIndexFinder(1);

    // Returns the last index on an array-like that passes a truth test.
    var findLastIndex = createPredicateIndexFinder(-1);

    // Use a comparator function to figure out the smallest index at which
    // an object should be inserted so as to maintain order. Uses binary search.
    function sortedIndex(array, obj, iteratee, context) {
      iteratee = cb(iteratee, context, 1);
      var value = iteratee(obj);
      var low = 0, high = getLength(array);
      while (low < high) {
        var mid = Math.floor((low + high) / 2);
        if (iteratee(array[mid]) < value) low = mid + 1; else high = mid;
      }
      return low;
    }

    // Internal function to generate the `_.indexOf` and `_.lastIndexOf` functions.
    function createIndexFinder(dir, predicateFind, sortedIndex) {
      return function(array, item, idx) {
        var i = 0, length = getLength(array);
        if (typeof idx == 'number') {
          if (dir > 0) {
            i = idx >= 0 ? idx : Math.max(idx + length, i);
          } else {
            length = idx >= 0 ? Math.min(idx + 1, length) : idx + length + 1;
          }
        } else if (sortedIndex && idx && length) {
          idx = sortedIndex(array, item);
          return array[idx] === item ? idx : -1;
        }
        if (item !== item) {
          idx = predicateFind(slice.call(array, i, length), isNaN$1);
          return idx >= 0 ? idx + i : -1;
        }
        for (idx = dir > 0 ? i : length - 1; idx >= 0 && idx < length; idx += dir) {
          if (array[idx] === item) return idx;
        }
        return -1;
      };
    }

    // Return the position of the first occurrence of an item in an array,
    // or -1 if the item is not included in the array.
    // If the array is large and already in sort order, pass `true`
    // for **isSorted** to use binary search.
    var indexOf = createIndexFinder(1, findIndex, sortedIndex);

    // Return the position of the last occurrence of an item in an array,
    // or -1 if the item is not included in the array.
    var lastIndexOf = createIndexFinder(-1, findLastIndex);

    // Return the first value which passes a truth test.
    function find(obj, predicate, context) {
      var keyFinder = isArrayLike(obj) ? findIndex : findKey;
      var key = keyFinder(obj, predicate, context);
      if (key !== void 0 && key !== -1) return obj[key];
    }

    // Convenience version of a common use case of `_.find`: getting the first
    // object containing specific `key:value` pairs.
    function findWhere(obj, attrs) {
      return find(obj, matcher(attrs));
    }

    // The cornerstone for collection functions, an `each`
    // implementation, aka `forEach`.
    // Handles raw objects in addition to array-likes. Treats all
    // sparse array-likes as if they were dense.
    function each(obj, iteratee, context) {
      iteratee = optimizeCb(iteratee, context);
      var i, length;
      if (isArrayLike(obj)) {
        for (i = 0, length = obj.length; i < length; i++) {
          iteratee(obj[i], i, obj);
        }
      } else {
        var _keys = keys(obj);
        for (i = 0, length = _keys.length; i < length; i++) {
          iteratee(obj[_keys[i]], _keys[i], obj);
        }
      }
      return obj;
    }

    // Return the results of applying the iteratee to each element.
    function map(obj, iteratee, context) {
      iteratee = cb(iteratee, context);
      var _keys = !isArrayLike(obj) && keys(obj),
          length = (_keys || obj).length,
          results = Array(length);
      for (var index = 0; index < length; index++) {
        var currentKey = _keys ? _keys[index] : index;
        results[index] = iteratee(obj[currentKey], currentKey, obj);
      }
      return results;
    }

    // Internal helper to create a reducing function, iterating left or right.
    function createReduce(dir) {
      // Wrap code that reassigns argument variables in a separate function than
      // the one that accesses `arguments.length` to avoid a perf hit. (#1991)
      var reducer = function(obj, iteratee, memo, initial) {
        var _keys = !isArrayLike(obj) && keys(obj),
            length = (_keys || obj).length,
            index = dir > 0 ? 0 : length - 1;
        if (!initial) {
          memo = obj[_keys ? _keys[index] : index];
          index += dir;
        }
        for (; index >= 0 && index < length; index += dir) {
          var currentKey = _keys ? _keys[index] : index;
          memo = iteratee(memo, obj[currentKey], currentKey, obj);
        }
        return memo;
      };

      return function(obj, iteratee, memo, context) {
        var initial = arguments.length >= 3;
        return reducer(obj, optimizeCb(iteratee, context, 4), memo, initial);
      };
    }

    // **Reduce** builds up a single result from a list of values, aka `inject`,
    // or `foldl`.
    var reduce = createReduce(1);

    // The right-associative version of reduce, also known as `foldr`.
    var reduceRight = createReduce(-1);

    // Return all the elements that pass a truth test.
    function filter(obj, predicate, context) {
      var results = [];
      predicate = cb(predicate, context);
      each(obj, function(value, index, list) {
        if (predicate(value, index, list)) results.push(value);
      });
      return results;
    }

    // Return all the elements for which a truth test fails.
    function reject(obj, predicate, context) {
      return filter(obj, negate(cb(predicate)), context);
    }

    // Determine whether all of the elements pass a truth test.
    function every(obj, predicate, context) {
      predicate = cb(predicate, context);
      var _keys = !isArrayLike(obj) && keys(obj),
          length = (_keys || obj).length;
      for (var index = 0; index < length; index++) {
        var currentKey = _keys ? _keys[index] : index;
        if (!predicate(obj[currentKey], currentKey, obj)) return false;
      }
      return true;
    }

    // Determine if at least one element in the object passes a truth test.
    function some(obj, predicate, context) {
      predicate = cb(predicate, context);
      var _keys = !isArrayLike(obj) && keys(obj),
          length = (_keys || obj).length;
      for (var index = 0; index < length; index++) {
        var currentKey = _keys ? _keys[index] : index;
        if (predicate(obj[currentKey], currentKey, obj)) return true;
      }
      return false;
    }

    // Determine if the array or object contains a given item (using `===`).
    function contains(obj, item, fromIndex, guard) {
      if (!isArrayLike(obj)) obj = values(obj);
      if (typeof fromIndex != 'number' || guard) fromIndex = 0;
      return indexOf(obj, item, fromIndex) >= 0;
    }

    // Invoke a method (with arguments) on every item in a collection.
    var invoke = restArguments(function(obj, path, args) {
      var contextPath, func;
      if (isFunction$1(path)) {
        func = path;
      } else if (isArray(path)) {
        contextPath = path.slice(0, -1);
        path = path[path.length - 1];
      }
      return map(obj, function(context) {
        var method = func;
        if (!method) {
          if (contextPath && contextPath.length) {
            context = deepGet(context, contextPath);
          }
          if (context == null) return void 0;
          method = context[path];
        }
        return method == null ? method : method.apply(context, args);
      });
    });

    // Convenience version of a common use case of `_.map`: fetching a property.
    function pluck(obj, key) {
      return map(obj, property(key));
    }

    // Convenience version of a common use case of `_.filter`: selecting only
    // objects containing specific `key:value` pairs.
    function where(obj, attrs) {
      return filter(obj, matcher(attrs));
    }

    // Return the maximum element (or element-based computation).
    function max(obj, iteratee, context) {
      var result = -Infinity, lastComputed = -Infinity,
          value, computed;
      if (iteratee == null || typeof iteratee == 'number' && typeof obj[0] != 'object' && obj != null) {
        obj = isArrayLike(obj) ? obj : values(obj);
        for (var i = 0, length = obj.length; i < length; i++) {
          value = obj[i];
          if (value != null && value > result) {
            result = value;
          }
        }
      } else {
        iteratee = cb(iteratee, context);
        each(obj, function(v, index, list) {
          computed = iteratee(v, index, list);
          if (computed > lastComputed || computed === -Infinity && result === -Infinity) {
            result = v;
            lastComputed = computed;
          }
        });
      }
      return result;
    }

    // Return the minimum element (or element-based computation).
    function min(obj, iteratee, context) {
      var result = Infinity, lastComputed = Infinity,
          value, computed;
      if (iteratee == null || typeof iteratee == 'number' && typeof obj[0] != 'object' && obj != null) {
        obj = isArrayLike(obj) ? obj : values(obj);
        for (var i = 0, length = obj.length; i < length; i++) {
          value = obj[i];
          if (value != null && value < result) {
            result = value;
          }
        }
      } else {
        iteratee = cb(iteratee, context);
        each(obj, function(v, index, list) {
          computed = iteratee(v, index, list);
          if (computed < lastComputed || computed === Infinity && result === Infinity) {
            result = v;
            lastComputed = computed;
          }
        });
      }
      return result;
    }

    // Sample **n** random values from a collection using the modern version of the
    // [Fisher-Yates shuffle](https://en.wikipedia.org/wiki/Fisher–Yates_shuffle).
    // If **n** is not specified, returns a single random element.
    // The internal `guard` argument allows it to work with `_.map`.
    function sample(obj, n, guard) {
      if (n == null || guard) {
        if (!isArrayLike(obj)) obj = values(obj);
        return obj[random(obj.length - 1)];
      }
      var sample = isArrayLike(obj) ? clone(obj) : values(obj);
      var length = getLength(sample);
      n = Math.max(Math.min(n, length), 0);
      var last = length - 1;
      for (var index = 0; index < n; index++) {
        var rand = random(index, last);
        var temp = sample[index];
        sample[index] = sample[rand];
        sample[rand] = temp;
      }
      return sample.slice(0, n);
    }

    // Shuffle a collection.
    function shuffle(obj) {
      return sample(obj, Infinity);
    }

    // Sort the object's values by a criterion produced by an iteratee.
    function sortBy(obj, iteratee, context) {
      var index = 0;
      iteratee = cb(iteratee, context);
      return pluck(map(obj, function(value, key, list) {
        return {
          value: value,
          index: index++,
          criteria: iteratee(value, key, list)
        };
      }).sort(function(left, right) {
        var a = left.criteria;
        var b = right.criteria;
        if (a !== b) {
          if (a > b || a === void 0) return 1;
          if (a < b || b === void 0) return -1;
        }
        return left.index - right.index;
      }), 'value');
    }

    // An internal function used for aggregate "group by" operations.
    function group(behavior, partition) {
      return function(obj, iteratee, context) {
        var result = partition ? [[], []] : {};
        iteratee = cb(iteratee, context);
        each(obj, function(value, index) {
          var key = iteratee(value, index, obj);
          behavior(result, value, key);
        });
        return result;
      };
    }

    // Groups the object's values by a criterion. Pass either a string attribute
    // to group by, or a function that returns the criterion.
    var groupBy = group(function(result, value, key) {
      if (has(result, key)) result[key].push(value); else result[key] = [value];
    });

    // Indexes the object's values by a criterion, similar to `_.groupBy`, but for
    // when you know that your index values will be unique.
    var indexBy = group(function(result, value, key) {
      result[key] = value;
    });

    // Counts instances of an object that group by a certain criterion. Pass
    // either a string attribute to count by, or a function that returns the
    // criterion.
    var countBy = group(function(result, value, key) {
      if (has(result, key)) result[key]++; else result[key] = 1;
    });

    // Split a collection into two arrays: one whose elements all pass the given
    // truth test, and one whose elements all do not pass the truth test.
    var partition = group(function(result, value, pass) {
      result[pass ? 0 : 1].push(value);
    }, true);

    // Safely create a real, live array from anything iterable.
    var reStrSymbol = /[^\ud800-\udfff]|[\ud800-\udbff][\udc00-\udfff]|[\ud800-\udfff]/g;
    function toArray(obj) {
      if (!obj) return [];
      if (isArray(obj)) return slice.call(obj);
      if (isString(obj)) {
        // Keep surrogate pair characters together.
        return obj.match(reStrSymbol);
      }
      if (isArrayLike(obj)) return map(obj, identity);
      return values(obj);
    }

    // Return the number of elements in a collection.
    function size(obj) {
      if (obj == null) return 0;
      return isArrayLike(obj) ? obj.length : keys(obj).length;
    }

    // Internal `_.pick` helper function to determine whether `key` is an enumerable
    // property name of `obj`.
    function keyInObj(value, key, obj) {
      return key in obj;
    }

    // Return a copy of the object only containing the allowed properties.
    var pick = restArguments(function(obj, keys) {
      var result = {}, iteratee = keys[0];
      if (obj == null) return result;
      if (isFunction$1(iteratee)) {
        if (keys.length > 1) iteratee = optimizeCb(iteratee, keys[1]);
        keys = allKeys(obj);
      } else {
        iteratee = keyInObj;
        keys = flatten(keys, false, false);
        obj = Object(obj);
      }
      for (var i = 0, length = keys.length; i < length; i++) {
        var key = keys[i];
        var value = obj[key];
        if (iteratee(value, key, obj)) result[key] = value;
      }
      return result;
    });

    // Return a copy of the object without the disallowed properties.
    var omit = restArguments(function(obj, keys) {
      var iteratee = keys[0], context;
      if (isFunction$1(iteratee)) {
        iteratee = negate(iteratee);
        if (keys.length > 1) context = keys[1];
      } else {
        keys = map(flatten(keys, false, false), String);
        iteratee = function(value, key) {
          return !contains(keys, key);
        };
      }
      return pick(obj, iteratee, context);
    });

    // Returns everything but the last entry of the array. Especially useful on
    // the arguments object. Passing **n** will return all the values in
    // the array, excluding the last N.
    function initial(array, n, guard) {
      return slice.call(array, 0, Math.max(0, array.length - (n == null || guard ? 1 : n)));
    }

    // Get the first element of an array. Passing **n** will return the first N
    // values in the array. The **guard** check allows it to work with `_.map`.
    function first(array, n, guard) {
      if (array == null || array.length < 1) return n == null || guard ? void 0 : [];
      if (n == null || guard) return array[0];
      return initial(array, array.length - n);
    }

    // Returns everything but the first entry of the `array`. Especially useful on
    // the `arguments` object. Passing an **n** will return the rest N values in the
    // `array`.
    function rest(array, n, guard) {
      return slice.call(array, n == null || guard ? 1 : n);
    }

    // Get the last element of an array. Passing **n** will return the last N
    // values in the array.
    function last(array, n, guard) {
      if (array == null || array.length < 1) return n == null || guard ? void 0 : [];
      if (n == null || guard) return array[array.length - 1];
      return rest(array, Math.max(0, array.length - n));
    }

    // Trim out all falsy values from an array.
    function compact(array) {
      return filter(array, Boolean);
    }

    // Flatten out an array, either recursively (by default), or up to `depth`.
    // Passing `true` or `false` as `depth` means `1` or `Infinity`, respectively.
    function flatten$1(array, depth) {
      return flatten(array, depth, false);
    }

    // Take the difference between one array and a number of other arrays.
    // Only the elements present in just the first array will remain.
    var difference = restArguments(function(array, rest) {
      rest = flatten(rest, true, true);
      return filter(array, function(value){
        return !contains(rest, value);
      });
    });

    // Return a version of the array that does not contain the specified value(s).
    var without = restArguments(function(array, otherArrays) {
      return difference(array, otherArrays);
    });

    // Produce a duplicate-free version of the array. If the array has already
    // been sorted, you have the option of using a faster algorithm.
    // The faster algorithm will not work with an iteratee if the iteratee
    // is not a one-to-one function, so providing an iteratee will disable
    // the faster algorithm.
    function uniq(array, isSorted, iteratee, context) {
      if (!isBoolean(isSorted)) {
        context = iteratee;
        iteratee = isSorted;
        isSorted = false;
      }
      if (iteratee != null) iteratee = cb(iteratee, context);
      var result = [];
      var seen = [];
      for (var i = 0, length = getLength(array); i < length; i++) {
        var value = array[i],
            computed = iteratee ? iteratee(value, i, array) : value;
        if (isSorted && !iteratee) {
          if (!i || seen !== computed) result.push(value);
          seen = computed;
        } else if (iteratee) {
          if (!contains(seen, computed)) {
            seen.push(computed);
            result.push(value);
          }
        } else if (!contains(result, value)) {
          result.push(value);
        }
      }
      return result;
    }

    // Produce an array that contains the union: each distinct element from all of
    // the passed-in arrays.
    var union = restArguments(function(arrays) {
      return uniq(flatten(arrays, true, true));
    });

    // Produce an array that contains every item shared between all the
    // passed-in arrays.
    function intersection(array) {
      var result = [];
      var argsLength = arguments.length;
      for (var i = 0, length = getLength(array); i < length; i++) {
        var item = array[i];
        if (contains(result, item)) continue;
        var j;
        for (j = 1; j < argsLength; j++) {
          if (!contains(arguments[j], item)) break;
        }
        if (j === argsLength) result.push(item);
      }
      return result;
    }

    // Complement of zip. Unzip accepts an array of arrays and groups
    // each array's elements on shared indices.
    function unzip(array) {
      var length = array && max(array, getLength).length || 0;
      var result = Array(length);

      for (var index = 0; index < length; index++) {
        result[index] = pluck(array, index);
      }
      return result;
    }

    // Zip together multiple lists into a single array -- elements that share
    // an index go together.
    var zip = restArguments(unzip);

    // Converts lists into objects. Pass either a single array of `[key, value]`
    // pairs, or two parallel arrays of the same length -- one of keys, and one of
    // the corresponding values. Passing by pairs is the reverse of `_.pairs`.
    function object(list, values) {
      var result = {};
      for (var i = 0, length = getLength(list); i < length; i++) {
        if (values) {
          result[list[i]] = values[i];
        } else {
          result[list[i][0]] = list[i][1];
        }
      }
      return result;
    }

    // Generate an integer Array containing an arithmetic progression. A port of
    // the native Python `range()` function. See
    // [the Python documentation](https://docs.python.org/library/functions.html#range).
    function range(start, stop, step) {
      if (stop == null) {
        stop = start || 0;
        start = 0;
      }
      if (!step) {
        step = stop < start ? -1 : 1;
      }

      var length = Math.max(Math.ceil((stop - start) / step), 0);
      var range = Array(length);

      for (var idx = 0; idx < length; idx++, start += step) {
        range[idx] = start;
      }

      return range;
    }

    // Chunk a single array into multiple arrays, each containing `count` or fewer
    // items.
    function chunk(array, count) {
      if (count == null || count < 1) return [];
      var result = [];
      var i = 0, length = array.length;
      while (i < length) {
        result.push(slice.call(array, i, i += count));
      }
      return result;
    }

    // Helper function to continue chaining intermediate results.
    function chainResult(instance, obj) {
      return instance._chain ? _(obj).chain() : obj;
    }

    // Add your own custom functions to the Underscore object.
    function mixin(obj) {
      each(functions(obj), function(name) {
        var func = _[name] = obj[name];
        _.prototype[name] = function() {
          var args = [this._wrapped];
          push.apply(args, arguments);
          return chainResult(this, func.apply(_, args));
        };
      });
      return _;
    }

    // Add all mutator `Array` functions to the wrapper.
    each(['pop', 'push', 'reverse', 'shift', 'sort', 'splice', 'unshift'], function(name) {
      var method = ArrayProto[name];
      _.prototype[name] = function() {
        var obj = this._wrapped;
        if (obj != null) {
          method.apply(obj, arguments);
          if ((name === 'shift' || name === 'splice') && obj.length === 0) {
            delete obj[0];
          }
        }
        return chainResult(this, obj);
      };
    });

    // Add all accessor `Array` functions to the wrapper.
    each(['concat', 'join', 'slice'], function(name) {
      var method = ArrayProto[name];
      _.prototype[name] = function() {
        var obj = this._wrapped;
        if (obj != null) obj = method.apply(obj, arguments);
        return chainResult(this, obj);
      };
    });

    // Named Exports

    var allExports = /*#__PURE__*/Object.freeze({
        __proto__: null,
        VERSION: VERSION,
        restArguments: restArguments,
        isObject: isObject,
        isNull: isNull,
        isUndefined: isUndefined,
        isBoolean: isBoolean,
        isElement: isElement,
        isString: isString,
        isNumber: isNumber,
        isDate: isDate,
        isRegExp: isRegExp,
        isError: isError,
        isSymbol: isSymbol,
        isMap: isMap,
        isWeakMap: isWeakMap,
        isSet: isSet,
        isWeakSet: isWeakSet,
        isArrayBuffer: isArrayBuffer,
        isDataView: isDataView,
        isArray: isArray,
        isFunction: isFunction$1,
        isArguments: isArguments$1,
        isFinite: isFinite$1,
        isNaN: isNaN$1,
        isTypedArray: isTypedArray$1,
        isEmpty: isEmpty,
        isMatch: isMatch,
        isEqual: isEqual,
        keys: keys,
        allKeys: allKeys,
        values: values,
        pairs: pairs,
        invert: invert,
        functions: functions,
        methods: functions,
        extend: extend,
        extendOwn: extendOwn,
        assign: extendOwn,
        defaults: defaults,
        create: create,
        clone: clone,
        tap: tap,
        has: has$1,
        mapObject: mapObject,
        identity: identity,
        constant: constant,
        noop: noop$1,
        property: property,
        propertyOf: propertyOf,
        matcher: matcher,
        matches: matcher,
        times: times,
        random: random,
        now: now,
        escape: _escape,
        unescape: _unescape,
        templateSettings: templateSettings,
        template: template,
        result: result,
        uniqueId: uniqueId,
        chain: chain,
        iteratee: iteratee,
        partial: partial,
        bind: bind$1,
        bindAll: bindAll,
        memoize: memoize,
        delay: delay,
        defer: defer,
        throttle: throttle,
        debounce: debounce,
        wrap: wrap,
        negate: negate,
        compose: compose,
        after: after,
        before: before,
        once: once,
        findKey: findKey,
        findIndex: findIndex,
        findLastIndex: findLastIndex,
        sortedIndex: sortedIndex,
        indexOf: indexOf,
        lastIndexOf: lastIndexOf,
        find: find,
        detect: find,
        findWhere: findWhere,
        each: each,
        forEach: each,
        map: map,
        collect: map,
        reduce: reduce,
        foldl: reduce,
        inject: reduce,
        reduceRight: reduceRight,
        foldr: reduceRight,
        filter: filter,
        select: filter,
        reject: reject,
        every: every,
        all: every,
        some: some,
        any: some,
        contains: contains,
        includes: contains,
        include: contains,
        invoke: invoke,
        pluck: pluck,
        where: where,
        max: max,
        min: min,
        shuffle: shuffle,
        sample: sample,
        sortBy: sortBy,
        groupBy: groupBy,
        indexBy: indexBy,
        countBy: countBy,
        partition: partition,
        toArray: toArray,
        size: size,
        pick: pick,
        omit: omit,
        first: first,
        head: first,
        take: first,
        initial: initial,
        last: last,
        rest: rest,
        tail: rest,
        drop: rest,
        compact: compact,
        flatten: flatten$1,
        without: without,
        uniq: uniq,
        unique: uniq,
        union: union,
        intersection: intersection,
        difference: difference,
        unzip: unzip,
        transpose: unzip,
        zip: zip,
        object: object,
        range: range,
        chunk: chunk,
        mixin: mixin,
        'default': _
    });

    // Default Export

    // Add all of the Underscore functions to the wrapper object.
    var _$1 = mixin(allExports);
    // Legacy Node.js API.
    _$1._ = _$1;

    function isAttribute(fieldName) {
        return !["key", "name", "label"].includes(fieldName);
    }

    class Entity {

        constructor(data) {
            this.key = null;
            this.label = null;
            this.name = null;
            this.attributes = {};

            for (const [key, value] of Object.entries(data || {})) {
                if (isAttribute(key)) {
                    if (value === '' || value === null || value === undefined) continue;
                    if (value instanceof Array && value.length === 0) continue;
                    this.attributes[key] = value;
                } else {
                    this[key] = value;
                }
            }
        }
    }

    class Neighbor {

        constructor(trail, node) {
            const edge = trail.hops[0].edges[0];
            this.direction = edge.end === trail.end ? "outgoing" : "incoming";
            this.verb = edge.verb;
            this.key = node.key;
            this.label = node.label;
            this.name = node.name;
        }
    }

    class SearchRequest {
        constructor(q, labels, keys, traversal, page, pageSize) {
            pageSize = pageSize || 10;

            this.q = q || '';
            this.labels = labels || [];
            this.keys = keys || [];
            this.traversal = (traversal && traversal.steps) || [];
            this.limit = pageSize;
            this.offset = page * pageSize;
        }
    }

    const Comparison = {
        contains: "contains",
        exact: "exact",
        gt: "gt",
        gte: "gte",
        icontains: "icontains",
        iexact: "iexact",
        is_in: "is_in",
        lt: "lt",
        lte: "lte",
        not_equal: "not_equal",
        startswith: "startswith",
        istartswith: "istartswith",
        endswith: "endswith",
        iendswith: "iendswith",
        range: "range",
        regex: "regex",
        iregex: "iregex",
    };

    class FieldCriteria {
        
        constructor(field, compare = Comparison.exact, value = '') {
            this.field = field;
            this.compare = compare;
            this.value = value;
            this.type = "field";
        }
    }

    class Traversal {

        constructor() {
            this.steps = [];
        }

        addStep(step) {
            this.steps = [...this.steps, step];
        }

        walk(verb = null, direction = null, maxHops = 1, passthru = false) {
            const verbs = verb !== null ? [verb] : [];
            const directions = Boolean(direction)  ? [direction.toLowerCase()] : ["incoming", "outgoing"];

            this.addStep({
                verbs: verbs,
                directions: directions,
                max_hops: maxHops,
                passthru: passthru,
            });
        }

        include(criteria = [], all = false) {
            this.addStep({
                criteria: criteria,
                all: all,
                exclude: false,
            });
        }

        exclude(criteria = [], all = false) {
            this.addStep({
                criteria: criteria,
                all: all,
                exclude: true,
            });
        }
    }

    const baseURL = window.location.origin;
    const searchURL = baseURL + "/search";
    const getNodeURL = baseURL + "/nodes/";
    const getSchemaURL = baseURL + "/meta/schema";

    const defaultParams = {
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        },
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
    };

    class RequestManager {

        constructor() {
            this.isClear = true;
            this.lastPage = null;
            this.lastRequest = {};
        }

        isAvailable(page, nextRequest) {
            const isChanged = (page !== this.lastPage) || (!_$1.isEqual(nextRequest, this.lastRequest));
            return this.isClear && isChanged
        }

        start(page, thisRequest) {
            this.isClear = false;
            this.lastPage = page;
            this.lastRequest = {...thisRequest};
        }

        finish() {
            this.isClear = true;
        }

        async getSchema() {
            return await fetch(getSchemaURL, {
                ...defaultParams,
                method: "GET",
            })
                .then(response => {
                    return response.json()
                })
                .catch(async response => {
                    console.log(response);
                    return {}
                });
        }

        async getEntity(key) {
            const data = await fetch(getNodeURL + key, {
                ...defaultParams,
                method: "GET",
            })
                .then(response => {
                    return response.json()
                })
                .catch(async response => {
                    console.log(response);
                    return {}
                });

            return new Entity(data);

        }

        async getNeighbors(page, thisRequest) {
            this.start(page, thisRequest);

            let traversal = new Traversal();
            traversal.walk(thisRequest.verb, thisRequest.direction);

            if (thisRequest.name) {
                const criteria = new FieldCriteria("name", Comparison.icontains, thisRequest.name);
                traversal.include([criteria]);
            }

            if (thisRequest.label) {
                const criteria = new FieldCriteria("label", Comparison.exact, thisRequest.label);
                traversal.include([criteria]);
            }


            let keys = thisRequest.key ? [thisRequest.key] : [];
            const request = new SearchRequest(null, null, keys, traversal, page);
            const response = await this.doSearch(request);

            let nodes = new Map(response.nodes.map(node => [node.key, node]));
            let neighbors = response.trails.map(trail => new Neighbor(trail, nodes.get(trail.end)));

            this.finish();
            return neighbors;
        }

        async getEntities(page, thisRequest) {
            this.start(page, thisRequest);

            let traversal = new Traversal();

            let labels = thisRequest.label ? [thisRequest.label] : [];
            let keys = thisRequest.key ? [thisRequest.key] : [];

            if (Boolean(thisRequest.attribute)) {
                const criteria = new FieldCriteria(
                    thisRequest.attribute.name, Comparison.icontains, thisRequest.attribute.value
                );
                traversal.include([criteria]);
            }

            const request = new SearchRequest(thisRequest.name, labels, keys, traversal, page);
            const response = await this.doSearch(request);
            const entities = response.nodes.map(data => new Entity(data));

            this.finish();
            return entities;
        }

        async doSearch(request) {
            const body = JSON.stringify(request);

            return await fetch(searchURL, {
                ...defaultParams,
                method: "POST",
                body: body,
            })
                .then(response => {
                    return response.json()
                })
                .catch(async response => {
                    console.log(response);
                    return {nodes: [], trails: []};
                });
        }
    }

    /* src/Menu.svelte generated by Svelte v3.24.1 */

    const file = "src/Menu.svelte";

    function create_fragment(ctx) {
    	let div1;
    	let div0;
    	let i;
    	let t0;
    	let a0;
    	let t2;
    	let a1;
    	let t4;
    	let a2;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			div1 = element("div");
    			div0 = element("div");
    			i = element("i");
    			t0 = space();
    			a0 = element("a");
    			a0.textContent = "Admin";
    			t2 = space();
    			a1 = element("a");
    			a1.textContent = "API";
    			t4 = space();
    			a2 = element("a");
    			a2.textContent = "Docs";
    			attr_dev(i, "class", "large lightbulb outline icon");
    			add_location(i, file, 14, 6, 280);
    			attr_dev(div0, "class", "item");
    			add_location(div0, file, 13, 2, 255);
    			attr_dev(a0, "id", "admin");
    			attr_dev(a0, "class", "active item");
    			add_location(a0, file, 16, 2, 336);
    			attr_dev(a1, "id", "api");
    			attr_dev(a1, "class", "item");
    			add_location(a1, file, 17, 2, 403);
    			attr_dev(a2, "id", "docs");
    			attr_dev(a2, "class", "item");
    			add_location(a2, file, 18, 2, 459);
    			attr_dev(div1, "class", "ui top menu svelte-1no5vn6");
    			add_location(div1, file, 12, 0, 227);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div1, anchor);
    			append_dev(div1, div0);
    			append_dev(div0, i);
    			append_dev(div1, t0);
    			append_dev(div1, a0);
    			append_dev(div1, t2);
    			append_dev(div1, a1);
    			append_dev(div1, t4);
    			append_dev(div1, a2);

    			if (!mounted) {
    				dispose = [
    					listen_dev(a0, "click", /*setChoice*/ ctx[0], false, false, false),
    					listen_dev(a1, "click", /*setChoice*/ ctx[0], false, false, false),
    					listen_dev(a2, "click", /*setChoice*/ ctx[0], false, false, false)
    				];

    				mounted = true;
    			}
    		},
    		p: noop,
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div1);
    			mounted = false;
    			run_all(dispose);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance($$self, $$props, $$invalidate) {
    	let { choice = "admin" } = $$props;

    	function setChoice(e) {
    		window.$(".menu .active").removeClass("active");
    		$$invalidate(1, choice = e.target.id);
    	}

    	const writable_props = ["choice"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<Menu> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("Menu", $$slots, []);

    	$$self.$$set = $$props => {
    		if ("choice" in $$props) $$invalidate(1, choice = $$props.choice);
    	};

    	$$self.$capture_state = () => ({ choice, setChoice });

    	$$self.$inject_state = $$props => {
    		if ("choice" in $$props) $$invalidate(1, choice = $$props.choice);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*choice*/ 2) {
    			 window.$("#" + choice).addClass("active");
    		}
    	};

    	return [setChoice, choice];
    }

    class Menu extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance, create_fragment, safe_not_equal, { choice: 1 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "Menu",
    			options,
    			id: create_fragment.name
    		});
    	}

    	get choice() {
    		throw new Error("<Menu>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set choice(value) {
    		throw new Error("<Menu>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/Bottom.svelte generated by Svelte v3.24.1 */

    const file$1 = "src/Bottom.svelte";

    function create_fragment$1(ctx) {
    	let div2;
    	let div1;
    	let div0;
    	let a0;
    	let i0;
    	let t0;
    	let a1;
    	let i1;
    	let t1;
    	let a2;
    	let i2;
    	let t2;
    	let a3;
    	let i3;
    	let t3;
    	let a4;
    	let i4;

    	const block = {
    		c: function create() {
    			div2 = element("div");
    			div1 = element("div");
    			div0 = element("div");
    			a0 = element("a");
    			i0 = element("i");
    			t0 = space();
    			a1 = element("a");
    			i1 = element("i");
    			t1 = space();
    			a2 = element("a");
    			i2 = element("i");
    			t2 = space();
    			a3 = element("a");
    			i3 = element("i");
    			t3 = space();
    			a4 = element("a");
    			i4 = element("i");
    			attr_dev(i0, "class", "large book open icon");
    			add_location(i0, file$1, 4, 16, 152);
    			attr_dev(a0, "href", "https://www.entitykb.org/");
    			add_location(a0, file$1, 3, 12, 99);
    			attr_dev(i1, "class", "large github icon");
    			add_location(i1, file$1, 7, 16, 287);
    			attr_dev(a1, "href", "https://github.com/genomoncology/entitykb");
    			add_location(a1, file$1, 6, 12, 218);
    			attr_dev(i2, "class", "large twitter icon");
    			add_location(i2, file$1, 10, 16, 411);
    			attr_dev(a2, "href", "https://twitter.com/genomoncology");
    			add_location(a2, file$1, 9, 12, 350);
    			attr_dev(i3, "class", "large linkedin icon");
    			add_location(i3, file$1, 13, 16, 549);
    			attr_dev(a3, "href", "https://www.linkedin.com/company/genomoncology");
    			add_location(a3, file$1, 12, 12, 475);
    			attr_dev(i4, "class", "large globe icon");
    			add_location(i4, file$1, 16, 16, 671);
    			attr_dev(a4, "href", "https://www.genomoncology.com");
    			add_location(a4, file$1, 15, 12, 614);
    			add_location(div0, file$1, 2, 8, 81);
    			attr_dev(div1, "class", "right item");
    			add_location(div1, file$1, 1, 4, 48);
    			attr_dev(div2, "class", "ui bottom fixed inverted menu");
    			add_location(div2, file$1, 0, 0, 0);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div2, anchor);
    			append_dev(div2, div1);
    			append_dev(div1, div0);
    			append_dev(div0, a0);
    			append_dev(a0, i0);
    			append_dev(div0, t0);
    			append_dev(div0, a1);
    			append_dev(a1, i1);
    			append_dev(div0, t1);
    			append_dev(div0, a2);
    			append_dev(a2, i2);
    			append_dev(div0, t2);
    			append_dev(div0, a3);
    			append_dev(a3, i3);
    			append_dev(div0, t3);
    			append_dev(div0, a4);
    			append_dev(a4, i4);
    		},
    		p: noop,
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div2);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$1.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$1($$self, $$props) {
    	const writable_props = [];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<Bottom> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("Bottom", $$slots, []);
    	return [];
    }

    class Bottom extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$1, create_fragment$1, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "Bottom",
    			options,
    			id: create_fragment$1.name
    		});
    	}
    }

    /* src/Pagination.svelte generated by Svelte v3.24.1 */
    const file$2 = "src/Pagination.svelte";

    function get_each_context(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[6] = list[i];
    	return child_ctx;
    }

    // (44:8) {:else}
    function create_else_block(ctx) {
    	let a;
    	let t0_value = /*item*/ ctx[6] + 1 + "";
    	let t0;
    	let t1;
    	let a_data_value_value;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			a = element("a");
    			t0 = text(t0_value);
    			t1 = space();
    			attr_dev(a, "class", "item svelte-947s4u");
    			attr_dev(a, "data-value", a_data_value_value = /*item*/ ctx[6]);
    			toggle_class(a, "active", /*item*/ ctx[6] === /*page*/ ctx[0]);
    			add_location(a, file$2, 44, 8, 1045);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, a, anchor);
    			append_dev(a, t0);
    			append_dev(a, t1);

    			if (!mounted) {
    				dispose = listen_dev(a, "click", /*onClick*/ ctx[2], false, false, false);
    				mounted = true;
    			}
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*items*/ 2 && t0_value !== (t0_value = /*item*/ ctx[6] + 1 + "")) set_data_dev(t0, t0_value);

    			if (dirty & /*items*/ 2 && a_data_value_value !== (a_data_value_value = /*item*/ ctx[6])) {
    				attr_dev(a, "data-value", a_data_value_value);
    			}

    			if (dirty & /*items, page*/ 3) {
    				toggle_class(a, "active", /*item*/ ctx[6] === /*page*/ ctx[0]);
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(a);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block.name,
    		type: "else",
    		source: "(44:8) {:else}",
    		ctx
    	});

    	return block;
    }

    // (42:8) {#if item === null}
    function create_if_block(ctx) {
    	let a;

    	const block = {
    		c: function create() {
    			a = element("a");
    			a.textContent = "...";
    			attr_dev(a, "class", "disabled item svelte-947s4u");
    			add_location(a, file$2, 42, 12, 988);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, a, anchor);
    		},
    		p: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(a);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block.name,
    		type: "if",
    		source: "(42:8) {#if item === null}",
    		ctx
    	});

    	return block;
    }

    // (41:4) {#each items as item}
    function create_each_block(ctx) {
    	let if_block_anchor;

    	function select_block_type(ctx, dirty) {
    		if (/*item*/ ctx[6] === null) return create_if_block;
    		return create_else_block;
    	}

    	let current_block_type = select_block_type(ctx);
    	let if_block = current_block_type(ctx);

    	const block = {
    		c: function create() {
    			if_block.c();
    			if_block_anchor = empty();
    		},
    		m: function mount(target, anchor) {
    			if_block.m(target, anchor);
    			insert_dev(target, if_block_anchor, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (current_block_type === (current_block_type = select_block_type(ctx)) && if_block) {
    				if_block.p(ctx, dirty);
    			} else {
    				if_block.d(1);
    				if_block = current_block_type(ctx);

    				if (if_block) {
    					if_block.c();
    					if_block.m(if_block_anchor.parentNode, if_block_anchor);
    				}
    			}
    		},
    		d: function destroy(detaching) {
    			if_block.d(detaching);
    			if (detaching) detach_dev(if_block_anchor);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block.name,
    		type: "each",
    		source: "(41:4) {#each items as item}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$2(ctx) {
    	let b;
    	let t1;
    	let div;
    	let each_value = /*items*/ ctx[1];
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block(get_each_context(ctx, each_value, i));
    	}

    	const block = {
    		c: function create() {
    			b = element("b");
    			b.textContent = "Page:";
    			t1 = space();
    			div = element("div");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			add_location(b, file$2, 37, 0, 870);
    			attr_dev(div, "class", "ui pagination tiny menu svelte-947s4u");
    			add_location(div, file$2, 39, 0, 884);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, b, anchor);
    			insert_dev(target, t1, anchor);
    			insert_dev(target, div, anchor);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(div, null);
    			}
    		},
    		p: function update(ctx, [dirty]) {
    			if (dirty & /*items, page, onClick*/ 7) {
    				each_value = /*items*/ ctx[1];
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(div, null);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value.length;
    			}
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(b);
    			if (detaching) detach_dev(t1);
    			if (detaching) detach_dev(div);
    			destroy_each(each_blocks, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$2.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$2($$self, $$props, $$invalidate) {
    	const dispatch = createEventDispatcher();
    	let { page = 0 } = $$props;
    	let items = [];
    	let addedNull = false;

    	function onClick(evt) {
    		$$invalidate(0, page = parseInt(evt.target.attributes["data-value"].value));
    	}

    	function changePage() {
    		$$invalidate(1, items = []);
    		let addedNull = false;

    		for (let i = 0; i <= page; i++) {
    			if (i < 4) {
    				items.push(i);
    			} else if (page - i < 4) {
    				items.push(i);
    			} else if (!addedNull) {
    				addedNull = true;
    				items.push(null);
    			}
    		}

    		items.push(page + 1);

    		while (items.length < 10) {
    			items.push(null);
    		}

    		dispatch("update", { "name": "page", "value": page });
    	}

    	const writable_props = ["page"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<Pagination> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("Pagination", $$slots, []);

    	$$self.$$set = $$props => {
    		if ("page" in $$props) $$invalidate(0, page = $$props.page);
    	};

    	$$self.$capture_state = () => ({
    		createEventDispatcher,
    		dispatch,
    		page,
    		items,
    		addedNull,
    		onClick,
    		changePage
    	});

    	$$self.$inject_state = $$props => {
    		if ("page" in $$props) $$invalidate(0, page = $$props.page);
    		if ("items" in $$props) $$invalidate(1, items = $$props.items);
    		if ("addedNull" in $$props) addedNull = $$props.addedNull;
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*page*/ 1) {
    			 changePage();
    		}
    	};

    	return [page, items, onClick];
    }

    class Pagination extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$2, create_fragment$2, safe_not_equal, { page: 0 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "Pagination",
    			options,
    			id: create_fragment$2.name
    		});
    	}

    	get page() {
    		throw new Error("<Pagination>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set page(value) {
    		throw new Error("<Pagination>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/ColumnFilter.svelte generated by Svelte v3.24.1 */
    const file$3 = "src/ColumnFilter.svelte";

    function get_each_context$1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[10] = list[i];
    	return child_ctx;
    }

    // (39:4) {:else}
    function create_else_block_1(ctx) {
    	let a;
    	let i;
    	let t0;
    	let t1;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			a = element("a");
    			i = element("i");
    			t0 = space();
    			t1 = text(/*display*/ ctx[1]);
    			attr_dev(i, "class", "blue filter icon svelte-1f5zqhf");
    			add_location(i, file$3, 40, 12, 1061);
    			attr_dev(a, "class", "clickable");
    			add_location(a, file$3, 39, 8, 1005);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, a, anchor);
    			append_dev(a, i);
    			append_dev(a, t0);
    			append_dev(a, t1);

    			if (!mounted) {
    				dispose = listen_dev(a, "click", /*openFilter*/ ctx[5], false, false, false);
    				mounted = true;
    			}
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*display*/ 2) set_data_dev(t1, /*display*/ ctx[1]);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(a);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block_1.name,
    		type: "else",
    		source: "(39:4) {:else}",
    		ctx
    	});

    	return block;
    }

    // (25:4) {#if inFilterMode}
    function create_if_block$1(ctx) {
    	let a;
    	let i;
    	let t;
    	let if_block_anchor;
    	let mounted;
    	let dispose;

    	function select_block_type_1(ctx, dirty) {
    		if (/*options*/ ctx[2]) return create_if_block_1;
    		return create_else_block$1;
    	}

    	let current_block_type = select_block_type_1(ctx);
    	let if_block = current_block_type(ctx);

    	const block = {
    		c: function create() {
    			a = element("a");
    			i = element("i");
    			t = space();
    			if_block.c();
    			if_block_anchor = empty();
    			attr_dev(i, "class", "red window close icon svelte-1f5zqhf");
    			add_location(i, file$3, 26, 12, 591);
    			attr_dev(a, "class", "clickable");
    			add_location(a, file$3, 25, 8, 533);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, a, anchor);
    			append_dev(a, i);
    			insert_dev(target, t, anchor);
    			if_block.m(target, anchor);
    			insert_dev(target, if_block_anchor, anchor);

    			if (!mounted) {
    				dispose = listen_dev(a, "click", /*cancelFilter*/ ctx[4], false, false, false);
    				mounted = true;
    			}
    		},
    		p: function update(ctx, dirty) {
    			if (current_block_type === (current_block_type = select_block_type_1(ctx)) && if_block) {
    				if_block.p(ctx, dirty);
    			} else {
    				if_block.d(1);
    				if_block = current_block_type(ctx);

    				if (if_block) {
    					if_block.c();
    					if_block.m(if_block_anchor.parentNode, if_block_anchor);
    				}
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(a);
    			if (detaching) detach_dev(t);
    			if_block.d(detaching);
    			if (detaching) detach_dev(if_block_anchor);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$1.name,
    		type: "if",
    		source: "(25:4) {#if inFilterMode}",
    		ctx
    	});

    	return block;
    }

    // (36:8) {:else}
    function create_else_block$1(ctx) {
    	let input;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			input = element("input");
    			attr_dev(input, "placeholder", /*display*/ ctx[1]);
    			input.autofocus = true;
    			add_location(input, file$3, 36, 12, 910);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, input, anchor);
    			set_input_value(input, /*value*/ ctx[0]);
    			input.focus();

    			if (!mounted) {
    				dispose = listen_dev(input, "input", /*input_input_handler*/ ctx[8]);
    				mounted = true;
    			}
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*display*/ 2) {
    				attr_dev(input, "placeholder", /*display*/ ctx[1]);
    			}

    			if (dirty & /*value, options*/ 5 && input.value !== /*value*/ ctx[0]) {
    				set_input_value(input, /*value*/ ctx[0]);
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(input);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block$1.name,
    		type: "else",
    		source: "(36:8) {:else}",
    		ctx
    	});

    	return block;
    }

    // (29:8) {#if options}
    function create_if_block_1(ctx) {
    	let select;
    	let option;
    	let t0;
    	let t1;
    	let mounted;
    	let dispose;
    	let each_value = /*options*/ ctx[2];
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block$1(get_each_context$1(ctx, each_value, i));
    	}

    	const block = {
    		c: function create() {
    			select = element("select");
    			option = element("option");
    			t0 = text("Any ");
    			t1 = text(/*display*/ ctx[1]);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			option.__value = "";
    			option.value = option.__value;
    			add_location(option, file$3, 30, 16, 720);
    			if (/*value*/ ctx[0] === void 0) add_render_callback(() => /*select_change_handler*/ ctx[7].call(select));
    			add_location(select, file$3, 29, 12, 676);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, select, anchor);
    			append_dev(select, option);
    			append_dev(option, t0);
    			append_dev(option, t1);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(select, null);
    			}

    			select_option(select, /*value*/ ctx[0]);

    			if (!mounted) {
    				dispose = listen_dev(select, "change", /*select_change_handler*/ ctx[7]);
    				mounted = true;
    			}
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*display*/ 2) set_data_dev(t1, /*display*/ ctx[1]);

    			if (dirty & /*options*/ 4) {
    				each_value = /*options*/ ctx[2];
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context$1(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block$1(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(select, null);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value.length;
    			}

    			if (dirty & /*value, options*/ 5) {
    				select_option(select, /*value*/ ctx[0]);
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(select);
    			destroy_each(each_blocks, detaching);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_1.name,
    		type: "if",
    		source: "(29:8) {#if options}",
    		ctx
    	});

    	return block;
    }

    // (32:12) {#each options as option}
    function create_each_block$1(ctx) {
    	let option;
    	let t_value = /*option*/ ctx[10] + "";
    	let t;
    	let option_value_value;

    	const block = {
    		c: function create() {
    			option = element("option");
    			t = text(t_value);
    			option.__value = option_value_value = /*option*/ ctx[10];
    			option.value = option.__value;
    			add_location(option, file$3, 32, 16, 814);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, option, anchor);
    			append_dev(option, t);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*options*/ 4 && t_value !== (t_value = /*option*/ ctx[10] + "")) set_data_dev(t, t_value);

    			if (dirty & /*options*/ 4 && option_value_value !== (option_value_value = /*option*/ ctx[10])) {
    				prop_dev(option, "__value", option_value_value);
    				option.value = option.__value;
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(option);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block$1.name,
    		type: "each",
    		source: "(32:12) {#each options as option}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$3(ctx) {
    	let div;

    	function select_block_type(ctx, dirty) {
    		if (/*inFilterMode*/ ctx[3]) return create_if_block$1;
    		return create_else_block_1;
    	}

    	let current_block_type = select_block_type(ctx);
    	let if_block = current_block_type(ctx);

    	const block = {
    		c: function create() {
    			div = element("div");
    			if_block.c();
    			attr_dev(div, "id", "column");
    			attr_dev(div, "class", "svelte-1f5zqhf");
    			add_location(div, file$3, 23, 0, 484);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			if_block.m(div, null);
    		},
    		p: function update(ctx, [dirty]) {
    			if (current_block_type === (current_block_type = select_block_type(ctx)) && if_block) {
    				if_block.p(ctx, dirty);
    			} else {
    				if_block.d(1);
    				if_block = current_block_type(ctx);

    				if (if_block) {
    					if_block.c();
    					if_block.m(div, null);
    				}
    			}
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    			if_block.d();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$3.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$3($$self, $$props, $$invalidate) {
    	const dispatch = createEventDispatcher();
    	let { name = null } = $$props;
    	let { value = null } = $$props;
    	let { display = null } = $$props;
    	let { options = "" } = $$props;
    	let inFilterMode = false;

    	const cancelFilter = () => {
    		$$invalidate(3, inFilterMode = false);
    		$$invalidate(0, value = "");
    	};

    	const openFilter = () => {
    		$$invalidate(3, inFilterMode = true);
    	};

    	const writable_props = ["name", "value", "display", "options"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<ColumnFilter> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("ColumnFilter", $$slots, []);

    	function select_change_handler() {
    		value = select_value(this);
    		$$invalidate(0, value);
    		$$invalidate(2, options);
    	}

    	function input_input_handler() {
    		value = this.value;
    		$$invalidate(0, value);
    		$$invalidate(2, options);
    	}

    	$$self.$$set = $$props => {
    		if ("name" in $$props) $$invalidate(6, name = $$props.name);
    		if ("value" in $$props) $$invalidate(0, value = $$props.value);
    		if ("display" in $$props) $$invalidate(1, display = $$props.display);
    		if ("options" in $$props) $$invalidate(2, options = $$props.options);
    	};

    	$$self.$capture_state = () => ({
    		createEventDispatcher,
    		dispatch,
    		name,
    		value,
    		display,
    		options,
    		inFilterMode,
    		cancelFilter,
    		openFilter
    	});

    	$$self.$inject_state = $$props => {
    		if ("name" in $$props) $$invalidate(6, name = $$props.name);
    		if ("value" in $$props) $$invalidate(0, value = $$props.value);
    		if ("display" in $$props) $$invalidate(1, display = $$props.display);
    		if ("options" in $$props) $$invalidate(2, options = $$props.options);
    		if ("inFilterMode" in $$props) $$invalidate(3, inFilterMode = $$props.inFilterMode);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*name, value*/ 65) {
    			 dispatch("update", { name, value });
    		}
    	};

    	return [
    		value,
    		display,
    		options,
    		inFilterMode,
    		cancelFilter,
    		openFilter,
    		name,
    		select_change_handler,
    		input_input_handler
    	];
    }

    class ColumnFilter extends SvelteComponentDev {
    	constructor(options) {
    		super(options);

    		init(this, options, instance$3, create_fragment$3, safe_not_equal, {
    			name: 6,
    			value: 0,
    			display: 1,
    			options: 2
    		});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "ColumnFilter",
    			options,
    			id: create_fragment$3.name
    		});
    	}

    	get name() {
    		throw new Error("<ColumnFilter>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set name(value) {
    		throw new Error("<ColumnFilter>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get value() {
    		throw new Error("<ColumnFilter>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set value(value) {
    		throw new Error("<ColumnFilter>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get display() {
    		throw new Error("<ColumnFilter>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set display(value) {
    		throw new Error("<ColumnFilter>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get options() {
    		throw new Error("<ColumnFilter>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set options(value) {
    		throw new Error("<ColumnFilter>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/AttributeFilter.svelte generated by Svelte v3.24.1 */
    const file$4 = "src/AttributeFilter.svelte";

    // (36:4) {:else}
    function create_else_block$2(ctx) {
    	let a;
    	let i;
    	let t;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			a = element("a");
    			i = element("i");
    			t = text("\n        Attributes");
    			attr_dev(i, "class", "blue filter icon svelte-1ds6of5");
    			add_location(i, file$4, 36, 33, 947);
    			add_location(a, file$4, 36, 8, 922);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, a, anchor);
    			append_dev(a, i);
    			insert_dev(target, t, anchor);

    			if (!mounted) {
    				dispose = listen_dev(a, "click", /*openFilter*/ ctx[4], false, false, false);
    				mounted = true;
    			}
    		},
    		p: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(a);
    			if (detaching) detach_dev(t);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block$2.name,
    		type: "else",
    		source: "(36:4) {:else}",
    		ctx
    	});

    	return block;
    }

    // (31:4) {#if inFilterMode}
    function create_if_block$2(ctx) {
    	let a;
    	let i;
    	let t0;
    	let input0;
    	let t1;
    	let input1;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			a = element("a");
    			i = element("i");
    			t0 = space();
    			input0 = element("input");
    			t1 = text("\n        ≈\n        ");
    			input1 = element("input");
    			attr_dev(i, "class", "red window close icon svelte-1ds6of5");
    			add_location(i, file$4, 31, 35, 720);
    			add_location(a, file$4, 31, 8, 693);
    			attr_dev(input0, "placeholder", "name");
    			input0.autofocus = true;
    			add_location(input0, file$4, 32, 8, 770);
    			attr_dev(input1, "placeholder", "value");
    			add_location(input1, file$4, 34, 8, 855);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, a, anchor);
    			append_dev(a, i);
    			insert_dev(target, t0, anchor);
    			insert_dev(target, input0, anchor);
    			set_input_value(input0, /*name*/ ctx[0]);
    			insert_dev(target, t1, anchor);
    			insert_dev(target, input1, anchor);
    			set_input_value(input1, /*value*/ ctx[1]);
    			input0.focus();

    			if (!mounted) {
    				dispose = [
    					listen_dev(a, "click", /*cancelFilter*/ ctx[3], false, false, false),
    					listen_dev(input0, "input", /*input0_input_handler*/ ctx[5]),
    					listen_dev(input1, "input", /*input1_input_handler*/ ctx[6])
    				];

    				mounted = true;
    			}
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*name*/ 1 && input0.value !== /*name*/ ctx[0]) {
    				set_input_value(input0, /*name*/ ctx[0]);
    			}

    			if (dirty & /*value*/ 2 && input1.value !== /*value*/ ctx[1]) {
    				set_input_value(input1, /*value*/ ctx[1]);
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(a);
    			if (detaching) detach_dev(t0);
    			if (detaching) detach_dev(input0);
    			if (detaching) detach_dev(t1);
    			if (detaching) detach_dev(input1);
    			mounted = false;
    			run_all(dispose);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$2.name,
    		type: "if",
    		source: "(31:4) {#if inFilterMode}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$4(ctx) {
    	let div;

    	function select_block_type(ctx, dirty) {
    		if (/*inFilterMode*/ ctx[2]) return create_if_block$2;
    		return create_else_block$2;
    	}

    	let current_block_type = select_block_type(ctx);
    	let if_block = current_block_type(ctx);

    	const block = {
    		c: function create() {
    			div = element("div");
    			if_block.c();
    			attr_dev(div, "id", "column");
    			attr_dev(div, "class", "svelte-1ds6of5");
    			add_location(div, file$4, 29, 0, 644);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			if_block.m(div, null);
    		},
    		p: function update(ctx, [dirty]) {
    			if (current_block_type === (current_block_type = select_block_type(ctx)) && if_block) {
    				if_block.p(ctx, dirty);
    			} else {
    				if_block.d(1);
    				if_block = current_block_type(ctx);

    				if (if_block) {
    					if_block.c();
    					if_block.m(div, null);
    				}
    			}
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    			if_block.d();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$4.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$4($$self, $$props, $$invalidate) {
    	const dispatch = createEventDispatcher();
    	let name = "";
    	let value = "";
    	let inFilterMode = false;

    	const cancelFilter = () => {
    		$$invalidate(2, inFilterMode = false);
    		$$invalidate(0, name = "");
    		$$invalidate(1, value = "");
    	};

    	const openFilter = () => {
    		$$invalidate(2, inFilterMode = true);
    	};

    	const updateFilterValue = () => {
    		let data = null;

    		if (Boolean(name) && Boolean(value)) {
    			data = { name, value };
    		}

    		dispatch("update", { "name": "attribute", "value": data });
    	};

    	const writable_props = [];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<AttributeFilter> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("AttributeFilter", $$slots, []);

    	function input0_input_handler() {
    		name = this.value;
    		$$invalidate(0, name);
    	}

    	function input1_input_handler() {
    		value = this.value;
    		$$invalidate(1, value);
    	}

    	$$self.$capture_state = () => ({
    		createEventDispatcher,
    		dispatch,
    		name,
    		value,
    		inFilterMode,
    		cancelFilter,
    		openFilter,
    		updateFilterValue
    	});

    	$$self.$inject_state = $$props => {
    		if ("name" in $$props) $$invalidate(0, name = $$props.name);
    		if ("value" in $$props) $$invalidate(1, value = $$props.value);
    		if ("inFilterMode" in $$props) $$invalidate(2, inFilterMode = $$props.inFilterMode);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*name, value*/ 3) {
    			 updateFilterValue();
    		}
    	};

    	return [
    		name,
    		value,
    		inFilterMode,
    		cancelFilter,
    		openFilter,
    		input0_input_handler,
    		input1_input_handler
    	];
    }

    class AttributeFilter extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$4, create_fragment$4, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "AttributeFilter",
    			options,
    			id: create_fragment$4.name
    		});
    	}
    }

    /* src/ListView.svelte generated by Svelte v3.24.1 */

    const { Object: Object_1 } = globals;
    const file$5 = "src/ListView.svelte";

    function get_each_context_2(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[18] = list[i];
    	return child_ctx;
    }

    function get_each_context_1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[14] = list[i][0];
    	child_ctx[15] = list[i][1];
    	return child_ctx;
    }

    function get_each_context$2(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[11] = list[i];
    	return child_ctx;
    }

    // (88:24) {:else}
    function create_else_block$3(ctx) {
    	let t_value = /*value*/ ctx[15] + "";
    	let t;

    	const block = {
    		c: function create() {
    			t = text(t_value);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, t, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*entities*/ 1 && t_value !== (t_value = /*value*/ ctx[15] + "")) set_data_dev(t, t_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(t);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block$3.name,
    		type: "else",
    		source: "(88:24) {:else}",
    		ctx
    	});

    	return block;
    }

    // (81:24) {#if value instanceof Array}
    function create_if_block$3(ctx) {
    	let t;
    	let if_block_anchor;
    	let each_value_2 = /*value*/ ctx[15].slice(0, 5);
    	validate_each_argument(each_value_2);
    	let each_blocks = [];

    	for (let i = 0; i < each_value_2.length; i += 1) {
    		each_blocks[i] = create_each_block_2(get_each_context_2(ctx, each_value_2, i));
    	}

    	let if_block = /*value*/ ctx[15].length > 5 && create_if_block_1$1(ctx);

    	const block = {
    		c: function create() {
    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			t = space();
    			if (if_block) if_block.c();
    			if_block_anchor = empty();
    		},
    		m: function mount(target, anchor) {
    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(target, anchor);
    			}

    			insert_dev(target, t, anchor);
    			if (if_block) if_block.m(target, anchor);
    			insert_dev(target, if_block_anchor, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*Object, entities*/ 1) {
    				each_value_2 = /*value*/ ctx[15].slice(0, 5);
    				validate_each_argument(each_value_2);
    				let i;

    				for (i = 0; i < each_value_2.length; i += 1) {
    					const child_ctx = get_each_context_2(ctx, each_value_2, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block_2(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(t.parentNode, t);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value_2.length;
    			}

    			if (/*value*/ ctx[15].length > 5) {
    				if (if_block) {
    					if_block.p(ctx, dirty);
    				} else {
    					if_block = create_if_block_1$1(ctx);
    					if_block.c();
    					if_block.m(if_block_anchor.parentNode, if_block_anchor);
    				}
    			} else if (if_block) {
    				if_block.d(1);
    				if_block = null;
    			}
    		},
    		d: function destroy(detaching) {
    			destroy_each(each_blocks, detaching);
    			if (detaching) detach_dev(t);
    			if (if_block) if_block.d(detaching);
    			if (detaching) detach_dev(if_block_anchor);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$3.name,
    		type: "if",
    		source: "(81:24) {#if value instanceof Array}",
    		ctx
    	});

    	return block;
    }

    // (82:28) {#each value.slice(0, 5) as item}
    function create_each_block_2(ctx) {
    	let t_value = /*item*/ ctx[18] + "";
    	let t;
    	let br;

    	const block = {
    		c: function create() {
    			t = text(t_value);
    			br = element("br");
    			add_location(br, file$5, 82, 38, 2567);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, t, anchor);
    			insert_dev(target, br, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*entities*/ 1 && t_value !== (t_value = /*item*/ ctx[18] + "")) set_data_dev(t, t_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(t);
    			if (detaching) detach_dev(br);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block_2.name,
    		type: "each",
    		source: "(82:28) {#each value.slice(0, 5) as item}",
    		ctx
    	});

    	return block;
    }

    // (85:28) {#if value.length > 5}
    function create_if_block_1$1(ctx) {
    	let i;
    	let t0_value = /*value*/ ctx[15].length - 5 + "";
    	let t0;
    	let t1;

    	const block = {
    		c: function create() {
    			i = element("i");
    			t0 = text(t0_value);
    			t1 = text(" more...");
    			add_location(i, file$5, 85, 32, 2692);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, i, anchor);
    			append_dev(i, t0);
    			append_dev(i, t1);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*entities*/ 1 && t0_value !== (t0_value = /*value*/ ctx[15].length - 5 + "")) set_data_dev(t0, t0_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(i);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_1$1.name,
    		type: "if",
    		source: "(85:28) {#if value.length > 5}",
    		ctx
    	});

    	return block;
    }

    // (77:16) {#each Object.entries(entity.attributes).sort() as [name, value]}
    function create_each_block_1(ctx) {
    	let tr;
    	let td0;
    	let t0_value = /*name*/ ctx[14] + "";
    	let t0;
    	let t1;
    	let t2;
    	let td1;
    	let t3;

    	function select_block_type(ctx, dirty) {
    		if (/*value*/ ctx[15] instanceof Array) return create_if_block$3;
    		return create_else_block$3;
    	}

    	let current_block_type = select_block_type(ctx);
    	let if_block = current_block_type(ctx);

    	const block = {
    		c: function create() {
    			tr = element("tr");
    			td0 = element("td");
    			t0 = text(t0_value);
    			t1 = text(":");
    			t2 = space();
    			td1 = element("td");
    			if_block.c();
    			t3 = space();
    			attr_dev(td0, "class", "four wide field_name svelte-1ulg1cd");
    			add_location(td0, file$5, 78, 24, 2319);
    			attr_dev(td1, "class", "twelve wide");
    			add_location(td1, file$5, 79, 24, 2389);
    			attr_dev(tr, "class", "top aligned");
    			add_location(tr, file$5, 77, 20, 2270);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, tr, anchor);
    			append_dev(tr, td0);
    			append_dev(td0, t0);
    			append_dev(td0, t1);
    			append_dev(tr, t2);
    			append_dev(tr, td1);
    			if_block.m(td1, null);
    			append_dev(tr, t3);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*entities*/ 1 && t0_value !== (t0_value = /*name*/ ctx[14] + "")) set_data_dev(t0, t0_value);

    			if (current_block_type === (current_block_type = select_block_type(ctx)) && if_block) {
    				if_block.p(ctx, dirty);
    			} else {
    				if_block.d(1);
    				if_block = current_block_type(ctx);

    				if (if_block) {
    					if_block.c();
    					if_block.m(td1, null);
    				}
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(tr);
    			if_block.d();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block_1.name,
    		type: "each",
    		source: "(77:16) {#each Object.entries(entity.attributes).sort() as [name, value]}",
    		ctx
    	});

    	return block;
    }

    // (70:4) {#each entities as entity}
    function create_each_block$2(ctx) {
    	let tr;
    	let td0;
    	let t0_value = /*entity*/ ctx[11].name + "";
    	let t0;
    	let t1;
    	let td1;
    	let t2_value = /*entity*/ ctx[11].label + "";
    	let t2;
    	let t3;
    	let td2;
    	let t4_value = /*entity*/ ctx[11].key + "";
    	let t4;
    	let t5;
    	let td3;
    	let table;
    	let t6;
    	let mounted;
    	let dispose;
    	let each_value_1 = Object.entries(/*entity*/ ctx[11].attributes).sort();
    	validate_each_argument(each_value_1);
    	let each_blocks = [];

    	for (let i = 0; i < each_value_1.length; i += 1) {
    		each_blocks[i] = create_each_block_1(get_each_context_1(ctx, each_value_1, i));
    	}

    	const block = {
    		c: function create() {
    			tr = element("tr");
    			td0 = element("td");
    			t0 = text(t0_value);
    			t1 = space();
    			td1 = element("td");
    			t2 = text(t2_value);
    			t3 = space();
    			td2 = element("td");
    			t4 = text(t4_value);
    			t5 = space();
    			td3 = element("td");
    			table = element("table");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			t6 = space();
    			add_location(td0, file$5, 71, 12, 1990);
    			add_location(td1, file$5, 72, 12, 2025);
    			add_location(td2, file$5, 73, 12, 2061);
    			attr_dev(table, "class", "ui compact celled table top aligned");
    			add_location(table, file$5, 75, 16, 2116);
    			add_location(td3, file$5, 74, 12, 2095);
    			add_location(tr, file$5, 70, 8, 1942);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, tr, anchor);
    			append_dev(tr, td0);
    			append_dev(td0, t0);
    			append_dev(tr, t1);
    			append_dev(tr, td1);
    			append_dev(td1, t2);
    			append_dev(tr, t3);
    			append_dev(tr, td2);
    			append_dev(td2, t4);
    			append_dev(tr, t5);
    			append_dev(tr, td3);
    			append_dev(td3, table);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(table, null);
    			}

    			append_dev(tr, t6);

    			if (!mounted) {
    				dispose = listen_dev(
    					tr,
    					"click",
    					function () {
    						if (is_function(/*openRow*/ ctx[3](/*entity*/ ctx[11].key))) /*openRow*/ ctx[3](/*entity*/ ctx[11].key).apply(this, arguments);
    					},
    					false,
    					false,
    					false
    				);

    				mounted = true;
    			}
    		},
    		p: function update(new_ctx, dirty) {
    			ctx = new_ctx;
    			if (dirty & /*entities*/ 1 && t0_value !== (t0_value = /*entity*/ ctx[11].name + "")) set_data_dev(t0, t0_value);
    			if (dirty & /*entities*/ 1 && t2_value !== (t2_value = /*entity*/ ctx[11].label + "")) set_data_dev(t2, t2_value);
    			if (dirty & /*entities*/ 1 && t4_value !== (t4_value = /*entity*/ ctx[11].key + "")) set_data_dev(t4, t4_value);

    			if (dirty & /*Object, entities, Array*/ 1) {
    				each_value_1 = Object.entries(/*entity*/ ctx[11].attributes).sort();
    				validate_each_argument(each_value_1);
    				let i;

    				for (i = 0; i < each_value_1.length; i += 1) {
    					const child_ctx = get_each_context_1(ctx, each_value_1, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block_1(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(table, null);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value_1.length;
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(tr);
    			destroy_each(each_blocks, detaching);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block$2.name,
    		type: "each",
    		source: "(70:4) {#each entities as entity}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$5(ctx) {
    	let div2;
    	let div0;
    	let t0;
    	let div1;
    	let pagination;
    	let updating_page;
    	let t1;
    	let table;
    	let thead;
    	let tr;
    	let th0;
    	let columnfilter0;
    	let t2;
    	let th1;
    	let columnfilter1;
    	let t3;
    	let th2;
    	let columnfilter2;
    	let t4;
    	let th3;
    	let attributefilter;
    	let t5;
    	let tbody;
    	let current;

    	function pagination_page_binding(value) {
    		/*pagination_page_binding*/ ctx[7].call(null, value);
    	}

    	let pagination_props = {};

    	if (/*page*/ ctx[1] !== void 0) {
    		pagination_props.page = /*page*/ ctx[1];
    	}

    	pagination = new Pagination({ props: pagination_props, $$inline: true });
    	binding_callbacks.push(() => bind(pagination, "page", pagination_page_binding));

    	columnfilter0 = new ColumnFilter({
    			props: { name: "name", display: "Name" },
    			$$inline: true
    		});

    	columnfilter0.$on("update", /*onUpdate*/ ctx[4]);

    	columnfilter1 = new ColumnFilter({
    			props: {
    				name: "label",
    				display: "Label",
    				options: /*labels*/ ctx[2]
    			},
    			$$inline: true
    		});

    	columnfilter1.$on("update", /*onUpdate*/ ctx[4]);

    	columnfilter2 = new ColumnFilter({
    			props: { name: "key", display: "Key" },
    			$$inline: true
    		});

    	columnfilter2.$on("update", /*onUpdate*/ ctx[4]);
    	attributefilter = new AttributeFilter({ $$inline: true });
    	attributefilter.$on("update", /*onUpdate*/ ctx[4]);
    	let each_value = /*entities*/ ctx[0];
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block$2(get_each_context$2(ctx, each_value, i));
    	}

    	const block = {
    		c: function create() {
    			div2 = element("div");
    			div0 = element("div");
    			t0 = space();
    			div1 = element("div");
    			create_component(pagination.$$.fragment);
    			t1 = space();
    			table = element("table");
    			thead = element("thead");
    			tr = element("tr");
    			th0 = element("th");
    			create_component(columnfilter0.$$.fragment);
    			t2 = space();
    			th1 = element("th");
    			create_component(columnfilter1.$$.fragment);
    			t3 = space();
    			th2 = element("th");
    			create_component(columnfilter2.$$.fragment);
    			t4 = space();
    			th3 = element("th");
    			create_component(attributefilter.$$.fragment);
    			t5 = space();
    			tbody = element("tbody");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			attr_dev(div0, "class", "eight wide column");
    			add_location(div0, file$5, 40, 4, 1029);
    			attr_dev(div1, "class", "eight wide column right aligned");
    			add_location(div1, file$5, 42, 4, 1076);
    			attr_dev(div2, "class", "ui grid");
    			add_location(div2, file$5, 39, 0, 1003);
    			attr_dev(th0, "class", "two wide");
    			add_location(th0, file$5, 50, 8, 1299);
    			attr_dev(th1, "class", "two wide");
    			add_location(th1, file$5, 54, 8, 1445);
    			attr_dev(th2, "class", "two wide");
    			add_location(th2, file$5, 59, 8, 1636);
    			attr_dev(th3, "class", "four wide");
    			add_location(th3, file$5, 63, 8, 1779);
    			add_location(tr, file$5, 49, 4, 1286);
    			attr_dev(thead, "class", "full-width");
    			add_location(thead, file$5, 48, 4, 1255);
    			add_location(tbody, file$5, 68, 4, 1895);
    			attr_dev(table, "class", "ui compact selectable celled striped table top aligned");
    			add_location(table, file$5, 47, 0, 1180);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div2, anchor);
    			append_dev(div2, div0);
    			append_dev(div2, t0);
    			append_dev(div2, div1);
    			mount_component(pagination, div1, null);
    			insert_dev(target, t1, anchor);
    			insert_dev(target, table, anchor);
    			append_dev(table, thead);
    			append_dev(thead, tr);
    			append_dev(tr, th0);
    			mount_component(columnfilter0, th0, null);
    			append_dev(tr, t2);
    			append_dev(tr, th1);
    			mount_component(columnfilter1, th1, null);
    			append_dev(tr, t3);
    			append_dev(tr, th2);
    			mount_component(columnfilter2, th2, null);
    			append_dev(tr, t4);
    			append_dev(tr, th3);
    			mount_component(attributefilter, th3, null);
    			append_dev(table, t5);
    			append_dev(table, tbody);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(tbody, null);
    			}

    			current = true;
    		},
    		p: function update(ctx, [dirty]) {
    			const pagination_changes = {};

    			if (!updating_page && dirty & /*page*/ 2) {
    				updating_page = true;
    				pagination_changes.page = /*page*/ ctx[1];
    				add_flush_callback(() => updating_page = false);
    			}

    			pagination.$set(pagination_changes);
    			const columnfilter1_changes = {};
    			if (dirty & /*labels*/ 4) columnfilter1_changes.options = /*labels*/ ctx[2];
    			columnfilter1.$set(columnfilter1_changes);

    			if (dirty & /*openRow, entities, Object, Array*/ 9) {
    				each_value = /*entities*/ ctx[0];
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context$2(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block$2(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(tbody, null);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value.length;
    			}
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(pagination.$$.fragment, local);
    			transition_in(columnfilter0.$$.fragment, local);
    			transition_in(columnfilter1.$$.fragment, local);
    			transition_in(columnfilter2.$$.fragment, local);
    			transition_in(attributefilter.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(pagination.$$.fragment, local);
    			transition_out(columnfilter0.$$.fragment, local);
    			transition_out(columnfilter1.$$.fragment, local);
    			transition_out(columnfilter2.$$.fragment, local);
    			transition_out(attributefilter.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div2);
    			destroy_component(pagination);
    			if (detaching) detach_dev(t1);
    			if (detaching) detach_dev(table);
    			destroy_component(columnfilter0);
    			destroy_component(columnfilter1);
    			destroy_component(columnfilter2);
    			destroy_component(attributefilter);
    			destroy_each(each_blocks, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$5.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$5($$self, $$props, $$invalidate) {
    	let { schema } = $$props;
    	let { selectKey = null } = $$props;
    	const manager = new RequestManager();

    	const nextRequest = {
    		name: "",
    		label: "",
    		key: "",
    		attribute: null
    	};

    	let entities = [];
    	let page = 0;

    	onMount(() => {
    		refreshData();
    		setInterval(refreshData, 10);
    	});

    	const openRow = key => {
    		$$invalidate(5, selectKey = key);
    	};

    	const onUpdate = async event => {
    		nextRequest[event.detail.name] = event.detail.value;
    		$$invalidate(1, page = 0);
    	};

    	const refreshData = async () => {
    		if (manager.isAvailable(page, nextRequest)) {
    			$$invalidate(0, entities = await manager.getEntities(page, nextRequest));
    		}
    	};

    	const writable_props = ["schema", "selectKey"];

    	Object_1.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<ListView> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("ListView", $$slots, []);

    	function pagination_page_binding(value) {
    		page = value;
    		$$invalidate(1, page);
    	}

    	$$self.$$set = $$props => {
    		if ("schema" in $$props) $$invalidate(6, schema = $$props.schema);
    		if ("selectKey" in $$props) $$invalidate(5, selectKey = $$props.selectKey);
    	};

    	$$self.$capture_state = () => ({
    		onMount,
    		RequestManager,
    		Pagination,
    		ColumnFilter,
    		AttributeFilter,
    		schema,
    		selectKey,
    		manager,
    		nextRequest,
    		entities,
    		page,
    		openRow,
    		onUpdate,
    		refreshData,
    		labels
    	});

    	$$self.$inject_state = $$props => {
    		if ("schema" in $$props) $$invalidate(6, schema = $$props.schema);
    		if ("selectKey" in $$props) $$invalidate(5, selectKey = $$props.selectKey);
    		if ("entities" in $$props) $$invalidate(0, entities = $$props.entities);
    		if ("page" in $$props) $$invalidate(1, page = $$props.page);
    		if ("labels" in $$props) $$invalidate(2, labels = $$props.labels);
    	};

    	let labels;

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*schema*/ 64) {
    			 $$invalidate(2, labels = schema !== null && schema.labels || []);
    		}
    	};

    	return [
    		entities,
    		page,
    		labels,
    		openRow,
    		onUpdate,
    		selectKey,
    		schema,
    		pagination_page_binding
    	];
    }

    class ListView extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$5, create_fragment$5, safe_not_equal, { schema: 6, selectKey: 5 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "ListView",
    			options,
    			id: create_fragment$5.name
    		});

    		const { ctx } = this.$$;
    		const props = options.props || {};

    		if (/*schema*/ ctx[6] === undefined && !("schema" in props)) {
    			console.warn("<ListView> was created without expected prop 'schema'");
    		}
    	}

    	get schema() {
    		throw new Error("<ListView>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set schema(value) {
    		throw new Error("<ListView>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get selectKey() {
    		throw new Error("<ListView>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set selectKey(value) {
    		throw new Error("<ListView>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/DetailView.svelte generated by Svelte v3.24.1 */

    const { Object: Object_1$1 } = globals;
    const file$6 = "src/DetailView.svelte";

    function get_each_context$3(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[16] = list[i];
    	return child_ctx;
    }

    function get_each_context_2$1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[23] = list[i];
    	return child_ctx;
    }

    function get_each_context_1$1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[19] = list[i][0];
    	child_ctx[20] = list[i][1];
    	return child_ctx;
    }

    // (81:20) {:else}
    function create_else_block$4(ctx) {
    	let t_value = /*value*/ ctx[20] + "";
    	let t;

    	const block = {
    		c: function create() {
    			t = text(t_value);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, t, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*entity*/ 1 && t_value !== (t_value = /*value*/ ctx[20] + "")) set_data_dev(t, t_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(t);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block$4.name,
    		type: "else",
    		source: "(81:20) {:else}",
    		ctx
    	});

    	return block;
    }

    // (77:20) {#if value instanceof Array}
    function create_if_block$4(ctx) {
    	let each_1_anchor;
    	let each_value_2 = /*value*/ ctx[20];
    	validate_each_argument(each_value_2);
    	let each_blocks = [];

    	for (let i = 0; i < each_value_2.length; i += 1) {
    		each_blocks[i] = create_each_block_2$1(get_each_context_2$1(ctx, each_value_2, i));
    	}

    	const block = {
    		c: function create() {
    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			each_1_anchor = empty();
    		},
    		m: function mount(target, anchor) {
    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(target, anchor);
    			}

    			insert_dev(target, each_1_anchor, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*Object, entity*/ 1) {
    				each_value_2 = /*value*/ ctx[20];
    				validate_each_argument(each_value_2);
    				let i;

    				for (i = 0; i < each_value_2.length; i += 1) {
    					const child_ctx = get_each_context_2$1(ctx, each_value_2, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block_2$1(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(each_1_anchor.parentNode, each_1_anchor);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value_2.length;
    			}
    		},
    		d: function destroy(detaching) {
    			destroy_each(each_blocks, detaching);
    			if (detaching) detach_dev(each_1_anchor);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$4.name,
    		type: "if",
    		source: "(77:20) {#if value instanceof Array}",
    		ctx
    	});

    	return block;
    }

    // (78:20) {#each value as item}
    function create_each_block_2$1(ctx) {
    	let t_value = /*item*/ ctx[23] + "";
    	let t;
    	let br;

    	const block = {
    		c: function create() {
    			t = text(t_value);
    			br = element("br");
    			add_location(br, file$6, 78, 30, 2189);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, t, anchor);
    			insert_dev(target, br, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*entity*/ 1 && t_value !== (t_value = /*item*/ ctx[23] + "")) set_data_dev(t, t_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(t);
    			if (detaching) detach_dev(br);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block_2$1.name,
    		type: "each",
    		source: "(78:20) {#each value as item}",
    		ctx
    	});

    	return block;
    }

    // (73:12) {#each Object.entries(entity.attributes).sort() as [name, value]}
    function create_each_block_1$1(ctx) {
    	let tr;
    	let td0;
    	let t0_value = /*name*/ ctx[19] + "";
    	let t0;
    	let t1;
    	let td1;
    	let t2;

    	function select_block_type(ctx, dirty) {
    		if (/*value*/ ctx[20] instanceof Array) return create_if_block$4;
    		return create_else_block$4;
    	}

    	let current_block_type = select_block_type(ctx);
    	let if_block = current_block_type(ctx);

    	const block = {
    		c: function create() {
    			tr = element("tr");
    			td0 = element("td");
    			t0 = text(t0_value);
    			t1 = space();
    			td1 = element("td");
    			if_block.c();
    			t2 = space();
    			add_location(td0, file$6, 74, 16, 2031);
    			add_location(td1, file$6, 75, 16, 2063);
    			add_location(tr, file$6, 73, 12, 2010);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, tr, anchor);
    			append_dev(tr, td0);
    			append_dev(td0, t0);
    			append_dev(tr, t1);
    			append_dev(tr, td1);
    			if_block.m(td1, null);
    			append_dev(tr, t2);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*entity*/ 1 && t0_value !== (t0_value = /*name*/ ctx[19] + "")) set_data_dev(t0, t0_value);

    			if (current_block_type === (current_block_type = select_block_type(ctx)) && if_block) {
    				if_block.p(ctx, dirty);
    			} else {
    				if_block.d(1);
    				if_block = current_block_type(ctx);

    				if (if_block) {
    					if_block.c();
    					if_block.m(td1, null);
    				}
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(tr);
    			if_block.d();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block_1$1.name,
    		type: "each",
    		source: "(73:12) {#each Object.entries(entity.attributes).sort() as [name, value]}",
    		ctx
    	});

    	return block;
    }

    // (126:12) {#each neighbors as neighbor}
    function create_each_block$3(ctx) {
    	let tr;
    	let td0;
    	let t0_value = /*neighbor*/ ctx[16].direction + "";
    	let t0;
    	let t1;
    	let td1;
    	let t2_value = /*neighbor*/ ctx[16].verb + "";
    	let t2;
    	let t3;
    	let td2;
    	let t4_value = /*neighbor*/ ctx[16].name + "";
    	let t4;
    	let t5;
    	let td3;
    	let t6_value = /*neighbor*/ ctx[16].label + "";
    	let t6;
    	let t7;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			tr = element("tr");
    			td0 = element("td");
    			t0 = text(t0_value);
    			t1 = space();
    			td1 = element("td");
    			t2 = text(t2_value);
    			t3 = space();
    			td2 = element("td");
    			t4 = text(t4_value);
    			t5 = space();
    			td3 = element("td");
    			t6 = text(t6_value);
    			t7 = space();
    			add_location(td0, file$6, 127, 20, 3960);
    			add_location(td1, file$6, 128, 20, 4010);
    			add_location(td2, file$6, 129, 20, 4055);
    			add_location(td3, file$6, 130, 20, 4100);
    			add_location(tr, file$6, 126, 16, 3902);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, tr, anchor);
    			append_dev(tr, td0);
    			append_dev(td0, t0);
    			append_dev(tr, t1);
    			append_dev(tr, td1);
    			append_dev(td1, t2);
    			append_dev(tr, t3);
    			append_dev(tr, td2);
    			append_dev(td2, t4);
    			append_dev(tr, t5);
    			append_dev(tr, td3);
    			append_dev(td3, t6);
    			append_dev(tr, t7);

    			if (!mounted) {
    				dispose = listen_dev(
    					tr,
    					"click",
    					function () {
    						if (is_function(/*openRow*/ ctx[7](/*neighbor*/ ctx[16].key))) /*openRow*/ ctx[7](/*neighbor*/ ctx[16].key).apply(this, arguments);
    					},
    					false,
    					false,
    					false
    				);

    				mounted = true;
    			}
    		},
    		p: function update(new_ctx, dirty) {
    			ctx = new_ctx;
    			if (dirty & /*neighbors*/ 2 && t0_value !== (t0_value = /*neighbor*/ ctx[16].direction + "")) set_data_dev(t0, t0_value);
    			if (dirty & /*neighbors*/ 2 && t2_value !== (t2_value = /*neighbor*/ ctx[16].verb + "")) set_data_dev(t2, t2_value);
    			if (dirty & /*neighbors*/ 2 && t4_value !== (t4_value = /*neighbor*/ ctx[16].name + "")) set_data_dev(t4, t4_value);
    			if (dirty & /*neighbors*/ 2 && t6_value !== (t6_value = /*neighbor*/ ctx[16].label + "")) set_data_dev(t6, t6_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(tr);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block$3.name,
    		type: "each",
    		source: "(126:12) {#each neighbors as neighbor}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$6(ctx) {
    	let div5;
    	let div0;
    	let h30;
    	let t1;
    	let table0;
    	let tbody0;
    	let tr0;
    	let td0;
    	let t3;
    	let td1;
    	let t4_value = /*entity*/ ctx[0].key + "";
    	let t4;
    	let t5;
    	let tr1;
    	let td2;
    	let t7;
    	let td3;
    	let t8_value = /*entity*/ ctx[0].name + "";
    	let t8;
    	let t9;
    	let tr2;
    	let td4;
    	let t11;
    	let td5;
    	let t12_value = /*entity*/ ctx[0].label + "";
    	let t12;
    	let t13;
    	let t14;
    	let div4;
    	let div3;
    	let div1;
    	let h31;
    	let t16;
    	let div2;
    	let pagination;
    	let updating_page;
    	let t17;
    	let table1;
    	let thead;
    	let tr3;
    	let th0;
    	let columnfilter0;
    	let t18;
    	let th1;
    	let columnfilter1;
    	let t19;
    	let th2;
    	let columnfilter2;
    	let t20;
    	let th3;
    	let columnfilter3;
    	let t21;
    	let tbody1;
    	let current;
    	let each_value_1 = Object.entries(/*entity*/ ctx[0].attributes).sort();
    	validate_each_argument(each_value_1);
    	let each_blocks_1 = [];

    	for (let i = 0; i < each_value_1.length; i += 1) {
    		each_blocks_1[i] = create_each_block_1$1(get_each_context_1$1(ctx, each_value_1, i));
    	}

    	function pagination_page_binding(value) {
    		/*pagination_page_binding*/ ctx[10].call(null, value);
    	}

    	let pagination_props = {};

    	if (/*page*/ ctx[2] !== void 0) {
    		pagination_props.page = /*page*/ ctx[2];
    	}

    	pagination = new Pagination({ props: pagination_props, $$inline: true });
    	binding_callbacks.push(() => bind(pagination, "page", pagination_page_binding));

    	columnfilter0 = new ColumnFilter({
    			props: {
    				name: "direction",
    				display: "Direction",
    				options: /*directions*/ ctx[5]
    			},
    			$$inline: true
    		});

    	columnfilter0.$on("update", /*onUpdate*/ ctx[6]);

    	columnfilter1 = new ColumnFilter({
    			props: {
    				name: "verb",
    				display: "Verb",
    				options: /*verbs*/ ctx[4]
    			},
    			$$inline: true
    		});

    	columnfilter1.$on("update", /*onUpdate*/ ctx[6]);

    	columnfilter2 = new ColumnFilter({
    			props: { name: "name", display: "Name" },
    			$$inline: true
    		});

    	columnfilter2.$on("update", /*onUpdate*/ ctx[6]);

    	columnfilter3 = new ColumnFilter({
    			props: {
    				name: "label",
    				display: "Label",
    				options: /*labels*/ ctx[3]
    			},
    			$$inline: true
    		});

    	columnfilter3.$on("update", /*onUpdate*/ ctx[6]);
    	let each_value = /*neighbors*/ ctx[1];
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block$3(get_each_context$3(ctx, each_value, i));
    	}

    	const block = {
    		c: function create() {
    			div5 = element("div");
    			div0 = element("div");
    			h30 = element("h3");
    			h30.textContent = "Node Details";
    			t1 = space();
    			table0 = element("table");
    			tbody0 = element("tbody");
    			tr0 = element("tr");
    			td0 = element("td");
    			td0.textContent = "key";
    			t3 = space();
    			td1 = element("td");
    			t4 = text(t4_value);
    			t5 = space();
    			tr1 = element("tr");
    			td2 = element("td");
    			td2.textContent = "name";
    			t7 = space();
    			td3 = element("td");
    			t8 = text(t8_value);
    			t9 = space();
    			tr2 = element("tr");
    			td4 = element("td");
    			td4.textContent = "label";
    			t11 = space();
    			td5 = element("td");
    			t12 = text(t12_value);
    			t13 = space();

    			for (let i = 0; i < each_blocks_1.length; i += 1) {
    				each_blocks_1[i].c();
    			}

    			t14 = space();
    			div4 = element("div");
    			div3 = element("div");
    			div1 = element("div");
    			h31 = element("h3");
    			h31.textContent = "Relationships";
    			t16 = space();
    			div2 = element("div");
    			create_component(pagination.$$.fragment);
    			t17 = space();
    			table1 = element("table");
    			thead = element("thead");
    			tr3 = element("tr");
    			th0 = element("th");
    			create_component(columnfilter0.$$.fragment);
    			t18 = space();
    			th1 = element("th");
    			create_component(columnfilter1.$$.fragment);
    			t19 = space();
    			th2 = element("th");
    			create_component(columnfilter2.$$.fragment);
    			t20 = space();
    			th3 = element("th");
    			create_component(columnfilter3.$$.fragment);
    			t21 = space();
    			tbody1 = element("tbody");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			add_location(h30, file$6, 57, 8, 1453);
    			attr_dev(td0, "class", "two wide column");
    			add_location(td0, file$6, 61, 16, 1592);
    			attr_dev(td1, "class", "five wide column");
    			add_location(td1, file$6, 62, 16, 1645);
    			add_location(tr0, file$6, 60, 12, 1571);
    			add_location(td2, file$6, 65, 16, 1743);
    			add_location(td3, file$6, 66, 16, 1773);
    			add_location(tr1, file$6, 64, 12, 1722);
    			add_location(td4, file$6, 69, 16, 1847);
    			add_location(td5, file$6, 70, 16, 1878);
    			add_location(tr2, file$6, 68, 12, 1826);
    			add_location(tbody0, file$6, 59, 12, 1551);
    			attr_dev(table0, "class", "ui compact definition table top aligned");
    			add_location(table0, file$6, 58, 8, 1483);
    			attr_dev(div0, "class", "seven wide column");
    			add_location(div0, file$6, 56, 4, 1413);
    			add_location(h31, file$6, 92, 16, 2541);
    			attr_dev(div1, "class", "one wide column");
    			add_location(div1, file$6, 91, 12, 2495);
    			attr_dev(div2, "class", "fifteen wide column right aligned");
    			add_location(div2, file$6, 94, 12, 2595);
    			attr_dev(div3, "class", "ui grid");
    			add_location(div3, file$6, 90, 8, 2461);
    			attr_dev(th0, "class", "two wide");
    			attr_dev(th0, "nowrap", "nowrap");
    			add_location(th0, file$6, 102, 16, 2853);
    			attr_dev(th1, "class", "two wide");
    			attr_dev(th1, "nowrap", "nowrap");
    			add_location(th1, file$6, 108, 16, 3146);
    			attr_dev(th2, "class", "three wide");
    			attr_dev(th2, "nowrap", "nowrap");
    			add_location(th2, file$6, 113, 16, 3390);
    			attr_dev(th3, "class", "two wide");
    			add_location(th3, file$6, 117, 16, 3586);
    			add_location(tr3, file$6, 101, 12, 2832);
    			attr_dev(thead, "class", "full-width");
    			add_location(thead, file$6, 100, 12, 2793);
    			add_location(tbody1, file$6, 124, 12, 3836);
    			attr_dev(table1, "class", "ui compact striped celled table");
    			add_location(table1, file$6, 99, 8, 2733);
    			attr_dev(div4, "class", "nine wide column");
    			add_location(div4, file$6, 89, 4, 2422);
    			attr_dev(div5, "class", "ui grid");
    			add_location(div5, file$6, 55, 0, 1387);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div5, anchor);
    			append_dev(div5, div0);
    			append_dev(div0, h30);
    			append_dev(div0, t1);
    			append_dev(div0, table0);
    			append_dev(table0, tbody0);
    			append_dev(tbody0, tr0);
    			append_dev(tr0, td0);
    			append_dev(tr0, t3);
    			append_dev(tr0, td1);
    			append_dev(td1, t4);
    			append_dev(tbody0, t5);
    			append_dev(tbody0, tr1);
    			append_dev(tr1, td2);
    			append_dev(tr1, t7);
    			append_dev(tr1, td3);
    			append_dev(td3, t8);
    			append_dev(tbody0, t9);
    			append_dev(tbody0, tr2);
    			append_dev(tr2, td4);
    			append_dev(tr2, t11);
    			append_dev(tr2, td5);
    			append_dev(td5, t12);
    			append_dev(tbody0, t13);

    			for (let i = 0; i < each_blocks_1.length; i += 1) {
    				each_blocks_1[i].m(tbody0, null);
    			}

    			append_dev(div5, t14);
    			append_dev(div5, div4);
    			append_dev(div4, div3);
    			append_dev(div3, div1);
    			append_dev(div1, h31);
    			append_dev(div3, t16);
    			append_dev(div3, div2);
    			mount_component(pagination, div2, null);
    			append_dev(div4, t17);
    			append_dev(div4, table1);
    			append_dev(table1, thead);
    			append_dev(thead, tr3);
    			append_dev(tr3, th0);
    			mount_component(columnfilter0, th0, null);
    			append_dev(tr3, t18);
    			append_dev(tr3, th1);
    			mount_component(columnfilter1, th1, null);
    			append_dev(tr3, t19);
    			append_dev(tr3, th2);
    			mount_component(columnfilter2, th2, null);
    			append_dev(tr3, t20);
    			append_dev(tr3, th3);
    			mount_component(columnfilter3, th3, null);
    			append_dev(table1, t21);
    			append_dev(table1, tbody1);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(tbody1, null);
    			}

    			current = true;
    		},
    		p: function update(ctx, [dirty]) {
    			if ((!current || dirty & /*entity*/ 1) && t4_value !== (t4_value = /*entity*/ ctx[0].key + "")) set_data_dev(t4, t4_value);
    			if ((!current || dirty & /*entity*/ 1) && t8_value !== (t8_value = /*entity*/ ctx[0].name + "")) set_data_dev(t8, t8_value);
    			if ((!current || dirty & /*entity*/ 1) && t12_value !== (t12_value = /*entity*/ ctx[0].label + "")) set_data_dev(t12, t12_value);

    			if (dirty & /*Object, entity, Array*/ 1) {
    				each_value_1 = Object.entries(/*entity*/ ctx[0].attributes).sort();
    				validate_each_argument(each_value_1);
    				let i;

    				for (i = 0; i < each_value_1.length; i += 1) {
    					const child_ctx = get_each_context_1$1(ctx, each_value_1, i);

    					if (each_blocks_1[i]) {
    						each_blocks_1[i].p(child_ctx, dirty);
    					} else {
    						each_blocks_1[i] = create_each_block_1$1(child_ctx);
    						each_blocks_1[i].c();
    						each_blocks_1[i].m(tbody0, null);
    					}
    				}

    				for (; i < each_blocks_1.length; i += 1) {
    					each_blocks_1[i].d(1);
    				}

    				each_blocks_1.length = each_value_1.length;
    			}

    			const pagination_changes = {};

    			if (!updating_page && dirty & /*page*/ 4) {
    				updating_page = true;
    				pagination_changes.page = /*page*/ ctx[2];
    				add_flush_callback(() => updating_page = false);
    			}

    			pagination.$set(pagination_changes);
    			const columnfilter1_changes = {};
    			if (dirty & /*verbs*/ 16) columnfilter1_changes.options = /*verbs*/ ctx[4];
    			columnfilter1.$set(columnfilter1_changes);
    			const columnfilter3_changes = {};
    			if (dirty & /*labels*/ 8) columnfilter3_changes.options = /*labels*/ ctx[3];
    			columnfilter3.$set(columnfilter3_changes);

    			if (dirty & /*openRow, neighbors*/ 130) {
    				each_value = /*neighbors*/ ctx[1];
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context$3(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block$3(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(tbody1, null);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value.length;
    			}
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(pagination.$$.fragment, local);
    			transition_in(columnfilter0.$$.fragment, local);
    			transition_in(columnfilter1.$$.fragment, local);
    			transition_in(columnfilter2.$$.fragment, local);
    			transition_in(columnfilter3.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(pagination.$$.fragment, local);
    			transition_out(columnfilter0.$$.fragment, local);
    			transition_out(columnfilter1.$$.fragment, local);
    			transition_out(columnfilter2.$$.fragment, local);
    			transition_out(columnfilter3.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div5);
    			destroy_each(each_blocks_1, detaching);
    			destroy_component(pagination);
    			destroy_component(columnfilter0);
    			destroy_component(columnfilter1);
    			destroy_component(columnfilter2);
    			destroy_component(columnfilter3);
    			destroy_each(each_blocks, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$6.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$6($$self, $$props, $$invalidate) {
    	let { schema } = $$props;
    	let { selectKey = null } = $$props;
    	const manager = new RequestManager();

    	const defaults = {
    		direction: "",
    		verb: "",
    		name: "",
    		label: ""
    	};

    	const nextRequest = { ...defaults, key: selectKey };
    	let entity = new Entity({});
    	let neighbors = [];
    	let page = 0;
    	const directions = ["Incoming", "Outgoing"];

    	onMount(() => {
    		loadEntity();
    		loadNeighbors();
    		setInterval(loadNeighbors, 50);
    	});

    	const loadEntity = async () => {
    		$$invalidate(0, entity = await manager.getEntity(selectKey));
    	};

    	const loadNeighbors = async () => {
    		if (manager.isAvailable(page, nextRequest)) {
    			$$invalidate(1, neighbors = await manager.getNeighbors(page, nextRequest));
    		}
    	};

    	const onUpdate = async event => {
    		nextRequest[event.detail.name] = event.detail.value;
    		$$invalidate(2, page = 0);
    	};

    	const openRow = rowKey => {
    		$$invalidate(2, page = 0);
    		$$invalidate(8, selectKey = rowKey);
    		nextRequest["key"] = rowKey;
    		loadEntity();
    	};

    	const writable_props = ["schema", "selectKey"];

    	Object_1$1.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<DetailView> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("DetailView", $$slots, []);

    	function pagination_page_binding(value) {
    		page = value;
    		$$invalidate(2, page);
    	}

    	$$self.$$set = $$props => {
    		if ("schema" in $$props) $$invalidate(9, schema = $$props.schema);
    		if ("selectKey" in $$props) $$invalidate(8, selectKey = $$props.selectKey);
    	};

    	$$self.$capture_state = () => ({
    		onMount,
    		RequestManager,
    		Entity,
    		Pagination,
    		ColumnFilter,
    		schema,
    		selectKey,
    		manager,
    		defaults,
    		nextRequest,
    		entity,
    		neighbors,
    		page,
    		directions,
    		loadEntity,
    		loadNeighbors,
    		onUpdate,
    		openRow,
    		labels,
    		verbs
    	});

    	$$self.$inject_state = $$props => {
    		if ("schema" in $$props) $$invalidate(9, schema = $$props.schema);
    		if ("selectKey" in $$props) $$invalidate(8, selectKey = $$props.selectKey);
    		if ("entity" in $$props) $$invalidate(0, entity = $$props.entity);
    		if ("neighbors" in $$props) $$invalidate(1, neighbors = $$props.neighbors);
    		if ("page" in $$props) $$invalidate(2, page = $$props.page);
    		if ("labels" in $$props) $$invalidate(3, labels = $$props.labels);
    		if ("verbs" in $$props) $$invalidate(4, verbs = $$props.verbs);
    	};

    	let labels;
    	let verbs;

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*schema*/ 512) {
    			 $$invalidate(3, labels = schema !== null && schema.labels || []);
    		}

    		if ($$self.$$.dirty & /*schema*/ 512) {
    			 $$invalidate(4, verbs = schema !== null && schema.verbs || []);
    		}
    	};

    	return [
    		entity,
    		neighbors,
    		page,
    		labels,
    		verbs,
    		directions,
    		onUpdate,
    		openRow,
    		selectKey,
    		schema,
    		pagination_page_binding
    	];
    }

    class DetailView extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$6, create_fragment$6, safe_not_equal, { schema: 9, selectKey: 8 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "DetailView",
    			options,
    			id: create_fragment$6.name
    		});

    		const { ctx } = this.$$;
    		const props = options.props || {};

    		if (/*schema*/ ctx[9] === undefined && !("schema" in props)) {
    			console.warn("<DetailView> was created without expected prop 'schema'");
    		}
    	}

    	get schema() {
    		throw new Error("<DetailView>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set schema(value) {
    		throw new Error("<DetailView>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get selectKey() {
    		throw new Error("<DetailView>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set selectKey(value) {
    		throw new Error("<DetailView>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/App.svelte generated by Svelte v3.24.1 */
    const file$7 = "src/App.svelte";

    // (52:34) 
    function create_if_block_3(ctx) {
    	let iframe;
    	let iframe_src_value;

    	const block = {
    		c: function create() {
    			iframe = element("iframe");
    			attr_dev(iframe, "title", "Docs");
    			if (iframe.src !== (iframe_src_value = "https://www.entitykb.org/")) attr_dev(iframe, "src", iframe_src_value);
    			attr_dev(iframe, "class", "svelte-jbahxs");
    			add_location(iframe, file$7, 52, 8, 1258);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, iframe, anchor);
    		},
    		p: noop,
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(iframe);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_3.name,
    		type: "if",
    		source: "(52:34) ",
    		ctx
    	});

    	return block;
    }

    // (50:33) 
    function create_if_block_2(ctx) {
    	let iframe;
    	let iframe_src_value;

    	const block = {
    		c: function create() {
    			iframe = element("iframe");
    			attr_dev(iframe, "title", "Swagger API");
    			if (iframe.src !== (iframe_src_value = "/docs")) attr_dev(iframe, "src", iframe_src_value);
    			attr_dev(iframe, "class", "svelte-jbahxs");
    			add_location(iframe, file$7, 50, 8, 1165);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, iframe, anchor);
    		},
    		p: noop,
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(iframe);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_2.name,
    		type: "if",
    		source: "(50:33) ",
    		ctx
    	});

    	return block;
    }

    // (46:36) 
    function create_if_block_1$2(ctx) {
    	let div;
    	let detailview;
    	let updating_selectKey;
    	let current;

    	function detailview_selectKey_binding(value) {
    		/*detailview_selectKey_binding*/ ctx[5].call(null, value);
    	}

    	let detailview_props = { schema: /*schema*/ ctx[2] };

    	if (/*selectKey*/ ctx[1] !== void 0) {
    		detailview_props.selectKey = /*selectKey*/ ctx[1];
    	}

    	detailview = new DetailView({ props: detailview_props, $$inline: true });
    	binding_callbacks.push(() => bind(detailview, "selectKey", detailview_selectKey_binding));

    	const block = {
    		c: function create() {
    			div = element("div");
    			create_component(detailview.$$.fragment);
    			attr_dev(div, "id", "content");
    			attr_dev(div, "class", "svelte-jbahxs");
    			add_location(div, file$7, 46, 4, 1027);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			mount_component(detailview, div, null);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			const detailview_changes = {};
    			if (dirty & /*schema*/ 4) detailview_changes.schema = /*schema*/ ctx[2];

    			if (!updating_selectKey && dirty & /*selectKey*/ 2) {
    				updating_selectKey = true;
    				detailview_changes.selectKey = /*selectKey*/ ctx[1];
    				add_flush_callback(() => updating_selectKey = false);
    			}

    			detailview.$set(detailview_changes);
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(detailview.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(detailview.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    			destroy_component(detailview);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_1$2.name,
    		type: "if",
    		source: "(46:36) ",
    		ctx
    	});

    	return block;
    }

    // (42:4) {#if (choice === "admin")}
    function create_if_block$5(ctx) {
    	let div;
    	let listview;
    	let updating_selectKey;
    	let current;

    	function listview_selectKey_binding(value) {
    		/*listview_selectKey_binding*/ ctx[4].call(null, value);
    	}

    	let listview_props = { schema: /*schema*/ ctx[2] };

    	if (/*selectKey*/ ctx[1] !== void 0) {
    		listview_props.selectKey = /*selectKey*/ ctx[1];
    	}

    	listview = new ListView({ props: listview_props, $$inline: true });
    	binding_callbacks.push(() => bind(listview, "selectKey", listview_selectKey_binding));

    	const block = {
    		c: function create() {
    			div = element("div");
    			create_component(listview.$$.fragment);
    			attr_dev(div, "id", "content");
    			attr_dev(div, "class", "svelte-jbahxs");
    			add_location(div, file$7, 42, 4, 892);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			mount_component(listview, div, null);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			const listview_changes = {};
    			if (dirty & /*schema*/ 4) listview_changes.schema = /*schema*/ ctx[2];

    			if (!updating_selectKey && dirty & /*selectKey*/ 2) {
    				updating_selectKey = true;
    				listview_changes.selectKey = /*selectKey*/ ctx[1];
    				add_flush_callback(() => updating_selectKey = false);
    			}

    			listview.$set(listview_changes);
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(listview.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(listview.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    			destroy_component(listview);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$5.name,
    		type: "if",
    		source: "(42:4) {#if (choice === \\\"admin\\\")}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$7(ctx) {
    	let main;
    	let menu;
    	let updating_choice;
    	let t0;
    	let current_block_type_index;
    	let if_block;
    	let t1;
    	let bottom;
    	let current;

    	function menu_choice_binding(value) {
    		/*menu_choice_binding*/ ctx[3].call(null, value);
    	}

    	let menu_props = {};

    	if (/*choice*/ ctx[0] !== void 0) {
    		menu_props.choice = /*choice*/ ctx[0];
    	}

    	menu = new Menu({ props: menu_props, $$inline: true });
    	binding_callbacks.push(() => bind(menu, "choice", menu_choice_binding));
    	const if_block_creators = [create_if_block$5, create_if_block_1$2, create_if_block_2, create_if_block_3];
    	const if_blocks = [];

    	function select_block_type(ctx, dirty) {
    		if (/*choice*/ ctx[0] === "admin") return 0;
    		if (/*choice*/ ctx[0] === "detail") return 1;
    		if (/*choice*/ ctx[0] === "api") return 2;
    		if (/*choice*/ ctx[0] === "docs") return 3;
    		return -1;
    	}

    	if (~(current_block_type_index = select_block_type(ctx))) {
    		if_block = if_blocks[current_block_type_index] = if_block_creators[current_block_type_index](ctx);
    	}

    	bottom = new Bottom({ $$inline: true });

    	const block = {
    		c: function create() {
    			main = element("main");
    			create_component(menu.$$.fragment);
    			t0 = space();
    			if (if_block) if_block.c();
    			t1 = space();
    			create_component(bottom.$$.fragment);
    			add_location(main, file$7, 38, 0, 815);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, main, anchor);
    			mount_component(menu, main, null);
    			append_dev(main, t0);

    			if (~current_block_type_index) {
    				if_blocks[current_block_type_index].m(main, null);
    			}

    			append_dev(main, t1);
    			mount_component(bottom, main, null);
    			current = true;
    		},
    		p: function update(ctx, [dirty]) {
    			const menu_changes = {};

    			if (!updating_choice && dirty & /*choice*/ 1) {
    				updating_choice = true;
    				menu_changes.choice = /*choice*/ ctx[0];
    				add_flush_callback(() => updating_choice = false);
    			}

    			menu.$set(menu_changes);
    			let previous_block_index = current_block_type_index;
    			current_block_type_index = select_block_type(ctx);

    			if (current_block_type_index === previous_block_index) {
    				if (~current_block_type_index) {
    					if_blocks[current_block_type_index].p(ctx, dirty);
    				}
    			} else {
    				if (if_block) {
    					group_outros();

    					transition_out(if_blocks[previous_block_index], 1, 1, () => {
    						if_blocks[previous_block_index] = null;
    					});

    					check_outros();
    				}

    				if (~current_block_type_index) {
    					if_block = if_blocks[current_block_type_index];

    					if (!if_block) {
    						if_block = if_blocks[current_block_type_index] = if_block_creators[current_block_type_index](ctx);
    						if_block.c();
    					}

    					transition_in(if_block, 1);
    					if_block.m(main, t1);
    				} else {
    					if_block = null;
    				}
    			}
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(menu.$$.fragment, local);
    			transition_in(if_block);
    			transition_in(bottom.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(menu.$$.fragment, local);
    			transition_out(if_block);
    			transition_out(bottom.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(main);
    			destroy_component(menu);

    			if (~current_block_type_index) {
    				if_blocks[current_block_type_index].d();
    			}

    			destroy_component(bottom);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$7.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$7($$self, $$props, $$invalidate) {
    	let choice = "admin";
    	let selectKey = null;
    	let schema = null;
    	const manager = new RequestManager();

    	onMount(async () => {
    		$$invalidate(2, schema = await manager.getSchema());
    	});

    	const updateKey = () => {
    		if (selectKey !== null) {
    			$$invalidate(0, choice = "detail");
    		} else {
    			$$invalidate(0, choice = "admin");
    		}
    	};

    	const updateChoice = () => {
    		if (choice !== "detail") {
    			$$invalidate(1, selectKey = null);
    		}
    	};

    	const writable_props = [];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<App> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("App", $$slots, []);

    	function menu_choice_binding(value) {
    		choice = value;
    		$$invalidate(0, choice);
    	}

    	function listview_selectKey_binding(value) {
    		selectKey = value;
    		$$invalidate(1, selectKey);
    	}

    	function detailview_selectKey_binding(value) {
    		selectKey = value;
    		$$invalidate(1, selectKey);
    	}

    	$$self.$capture_state = () => ({
    		onMount,
    		RequestManager,
    		Menu,
    		Bottom,
    		ListView,
    		DetailView,
    		choice,
    		selectKey,
    		schema,
    		manager,
    		updateKey,
    		updateChoice
    	});

    	$$self.$inject_state = $$props => {
    		if ("choice" in $$props) $$invalidate(0, choice = $$props.choice);
    		if ("selectKey" in $$props) $$invalidate(1, selectKey = $$props.selectKey);
    		if ("schema" in $$props) $$invalidate(2, schema = $$props.schema);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*selectKey*/ 2) {
    			 updateKey();
    		}

    		if ($$self.$$.dirty & /*choice*/ 1) {
    			 updateChoice();
    		}
    	};

    	return [
    		choice,
    		selectKey,
    		schema,
    		menu_choice_binding,
    		listview_selectKey_binding,
    		detailview_selectKey_binding
    	];
    }

    class App extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$7, create_fragment$7, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "App",
    			options,
    			id: create_fragment$7.name
    		});
    	}
    }

    const app = new App({
    	target: document.body,
    	props: {
    	}
    });

    return app;

}());
//# sourceMappingURL=bundle.js.map
