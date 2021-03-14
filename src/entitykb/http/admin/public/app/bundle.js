
(function(l, r) { if (l.getElementById('livereloadscript')) return; r = l.createElement('script'); r.async = 1; r.src = '//' + (window.location.host || 'localhost').split(':')[0] + ':35729/livereload.js?snipver=1'; r.id = 'livereloadscript'; l.getElementsByTagName('head')[0].appendChild(r) })(window.document);
var app = (function () {
    'use strict';

    function noop() { }
    const identity = x => x;
    function assign(tar, src) {
        // @ts-ignore
        for (const k in src)
            tar[k] = src[k];
        return tar;
    }
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
    function validate_store(store, name) {
        if (store != null && typeof store.subscribe !== 'function') {
            throw new Error(`'${name}' is not a store with a 'subscribe' method`);
        }
    }
    function subscribe(store, ...callbacks) {
        if (store == null) {
            return noop;
        }
        const unsub = store.subscribe(...callbacks);
        return unsub.unsubscribe ? () => unsub.unsubscribe() : unsub;
    }
    function component_subscribe(component, store, callback) {
        component.$$.on_destroy.push(subscribe(store, callback));
    }
    function create_slot(definition, ctx, $$scope, fn) {
        if (definition) {
            const slot_ctx = get_slot_context(definition, ctx, $$scope, fn);
            return definition[0](slot_ctx);
        }
    }
    function get_slot_context(definition, ctx, $$scope, fn) {
        return definition[1] && fn
            ? assign($$scope.ctx.slice(), definition[1](fn(ctx)))
            : $$scope.ctx;
    }
    function get_slot_changes(definition, $$scope, dirty, fn) {
        if (definition[2] && fn) {
            const lets = definition[2](fn(dirty));
            if ($$scope.dirty === undefined) {
                return lets;
            }
            if (typeof lets === 'object') {
                const merged = [];
                const len = Math.max($$scope.dirty.length, lets.length);
                for (let i = 0; i < len; i += 1) {
                    merged[i] = $$scope.dirty[i] | lets[i];
                }
                return merged;
            }
            return $$scope.dirty | lets;
        }
        return $$scope.dirty;
    }
    function update_slot(slot, slot_definition, ctx, $$scope, dirty, get_slot_changes_fn, get_slot_context_fn) {
        const slot_changes = get_slot_changes(slot_definition, $$scope, dirty, get_slot_changes_fn);
        if (slot_changes) {
            const slot_context = get_slot_context(slot_definition, ctx, $$scope, get_slot_context_fn);
            slot.p(slot_context, slot_changes);
        }
    }
    function action_destroyer(action_result) {
        return action_result && is_function(action_result.destroy) ? action_result.destroy : noop;
    }

    const is_client = typeof window !== 'undefined';
    let now = is_client
        ? () => window.performance.now()
        : () => Date.now();
    let raf = is_client ? cb => requestAnimationFrame(cb) : noop;

    const tasks = new Set();
    function run_tasks(now) {
        tasks.forEach(task => {
            if (!task.c(now)) {
                tasks.delete(task);
                task.f();
            }
        });
        if (tasks.size !== 0)
            raf(run_tasks);
    }
    /**
     * Creates a new task that runs on each raf frame
     * until it returns a falsy value or is aborted
     */
    function loop(callback) {
        let task;
        if (tasks.size === 0)
            raf(run_tasks);
        return {
            promise: new Promise(fulfill => {
                tasks.add(task = { c: callback, f: fulfill });
            }),
            abort() {
                tasks.delete(task);
            }
        };
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
    function prevent_default(fn) {
        return function (event) {
            event.preventDefault();
            // @ts-ignore
            return fn.call(this, event);
        };
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

    const active_docs = new Set();
    let active = 0;
    // https://github.com/darkskyapp/string-hash/blob/master/index.js
    function hash(str) {
        let hash = 5381;
        let i = str.length;
        while (i--)
            hash = ((hash << 5) - hash) ^ str.charCodeAt(i);
        return hash >>> 0;
    }
    function create_rule(node, a, b, duration, delay, ease, fn, uid = 0) {
        const step = 16.666 / duration;
        let keyframes = '{\n';
        for (let p = 0; p <= 1; p += step) {
            const t = a + (b - a) * ease(p);
            keyframes += p * 100 + `%{${fn(t, 1 - t)}}\n`;
        }
        const rule = keyframes + `100% {${fn(b, 1 - b)}}\n}`;
        const name = `__svelte_${hash(rule)}_${uid}`;
        const doc = node.ownerDocument;
        active_docs.add(doc);
        const stylesheet = doc.__svelte_stylesheet || (doc.__svelte_stylesheet = doc.head.appendChild(element('style')).sheet);
        const current_rules = doc.__svelte_rules || (doc.__svelte_rules = {});
        if (!current_rules[name]) {
            current_rules[name] = true;
            stylesheet.insertRule(`@keyframes ${name} ${rule}`, stylesheet.cssRules.length);
        }
        const animation = node.style.animation || '';
        node.style.animation = `${animation ? `${animation}, ` : ``}${name} ${duration}ms linear ${delay}ms 1 both`;
        active += 1;
        return name;
    }
    function delete_rule(node, name) {
        const previous = (node.style.animation || '').split(', ');
        const next = previous.filter(name
            ? anim => anim.indexOf(name) < 0 // remove specific animation
            : anim => anim.indexOf('__svelte') === -1 // remove all Svelte animations
        );
        const deleted = previous.length - next.length;
        if (deleted) {
            node.style.animation = next.join(', ');
            active -= deleted;
            if (!active)
                clear_rules();
        }
    }
    function clear_rules() {
        raf(() => {
            if (active)
                return;
            active_docs.forEach(doc => {
                const stylesheet = doc.__svelte_stylesheet;
                let i = stylesheet.cssRules.length;
                while (i--)
                    stylesheet.deleteRule(i);
                doc.__svelte_rules = {};
            });
            active_docs.clear();
        });
    }

    function create_animation(node, from, fn, params) {
        if (!from)
            return noop;
        const to = node.getBoundingClientRect();
        if (from.left === to.left && from.right === to.right && from.top === to.top && from.bottom === to.bottom)
            return noop;
        const { delay = 0, duration = 300, easing = identity, 
        // @ts-ignore todo: should this be separated from destructuring? Or start/end added to public api and documentation?
        start: start_time = now() + delay, 
        // @ts-ignore todo:
        end = start_time + duration, tick = noop, css } = fn(node, { from, to }, params);
        let running = true;
        let started = false;
        let name;
        function start() {
            if (css) {
                name = create_rule(node, 0, 1, duration, delay, easing, css);
            }
            if (!delay) {
                started = true;
            }
        }
        function stop() {
            if (css)
                delete_rule(node, name);
            running = false;
        }
        loop(now => {
            if (!started && now >= start_time) {
                started = true;
            }
            if (started && now >= end) {
                tick(1, 0);
                stop();
            }
            if (!running) {
                return false;
            }
            if (started) {
                const p = now - start_time;
                const t = 0 + 1 * easing(p / duration);
                tick(t, 1 - t);
            }
            return true;
        });
        start();
        tick(0, 1);
        return stop;
    }
    function fix_position(node) {
        const style = getComputedStyle(node);
        if (style.position !== 'absolute' && style.position !== 'fixed') {
            const { width, height } = style;
            const a = node.getBoundingClientRect();
            node.style.position = 'absolute';
            node.style.width = width;
            node.style.height = height;
            add_transform(node, a);
        }
    }
    function add_transform(node, a) {
        const b = node.getBoundingClientRect();
        if (a.left !== b.left || a.top !== b.top) {
            const style = getComputedStyle(node);
            const transform = style.transform === 'none' ? '' : style.transform;
            node.style.transform = `${transform} translate(${a.left - b.left}px, ${a.top - b.top}px)`;
        }
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
    function afterUpdate(fn) {
        get_current_component().$$.after_update.push(fn);
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
    // TODO figure out if we still want to support
    // shorthand events, or if we want to implement
    // a real bubbling mechanism
    function bubble(component, event) {
        const callbacks = component.$$.callbacks[event.type];
        if (callbacks) {
            callbacks.slice().forEach(fn => fn(event));
        }
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
    function tick() {
        schedule_update();
        return resolved_promise;
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

    let promise;
    function wait() {
        if (!promise) {
            promise = Promise.resolve();
            promise.then(() => {
                promise = null;
            });
        }
        return promise;
    }
    function dispatch(node, direction, kind) {
        node.dispatchEvent(custom_event(`${direction ? 'intro' : 'outro'}${kind}`));
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
    const null_transition = { duration: 0 };
    function create_in_transition(node, fn, params) {
        let config = fn(node, params);
        let running = false;
        let animation_name;
        let task;
        let uid = 0;
        function cleanup() {
            if (animation_name)
                delete_rule(node, animation_name);
        }
        function go() {
            const { delay = 0, duration = 300, easing = identity, tick = noop, css } = config || null_transition;
            if (css)
                animation_name = create_rule(node, 0, 1, duration, delay, easing, css, uid++);
            tick(0, 1);
            const start_time = now() + delay;
            const end_time = start_time + duration;
            if (task)
                task.abort();
            running = true;
            add_render_callback(() => dispatch(node, true, 'start'));
            task = loop(now => {
                if (running) {
                    if (now >= end_time) {
                        tick(1, 0);
                        dispatch(node, true, 'end');
                        cleanup();
                        return running = false;
                    }
                    if (now >= start_time) {
                        const t = easing((now - start_time) / duration);
                        tick(t, 1 - t);
                    }
                }
                return running;
            });
        }
        let started = false;
        return {
            start() {
                if (started)
                    return;
                delete_rule(node);
                if (is_function(config)) {
                    config = config();
                    wait().then(go);
                }
                else {
                    go();
                }
            },
            invalidate() {
                started = false;
            },
            end() {
                if (running) {
                    cleanup();
                    running = false;
                }
            }
        };
    }
    function create_out_transition(node, fn, params) {
        let config = fn(node, params);
        let running = true;
        let animation_name;
        const group = outros;
        group.r += 1;
        function go() {
            const { delay = 0, duration = 300, easing = identity, tick = noop, css } = config || null_transition;
            if (css)
                animation_name = create_rule(node, 1, 0, duration, delay, easing, css);
            const start_time = now() + delay;
            const end_time = start_time + duration;
            add_render_callback(() => dispatch(node, false, 'start'));
            loop(now => {
                if (running) {
                    if (now >= end_time) {
                        tick(0, 1);
                        dispatch(node, false, 'end');
                        if (!--group.r) {
                            // this will result in `end()` being called,
                            // so we don't need to clean up here
                            run_all(group.c);
                        }
                        return false;
                    }
                    if (now >= start_time) {
                        const t = easing((now - start_time) / duration);
                        tick(1 - t, t);
                    }
                }
                return running;
            });
        }
        if (is_function(config)) {
            wait().then(() => {
                // @ts-ignore
                config = config();
                go();
            });
        }
        else {
            go();
        }
        return {
            end(reset) {
                if (reset && config.tick) {
                    config.tick(1, 0);
                }
                if (running) {
                    if (animation_name)
                        delete_rule(node, animation_name);
                    running = false;
                }
            }
        };
    }

    const globals = (typeof window !== 'undefined'
        ? window
        : typeof globalThis !== 'undefined'
            ? globalThis
            : global);
    function outro_and_destroy_block(block, lookup) {
        transition_out(block, 1, 1, () => {
            lookup.delete(block.key);
        });
    }
    function fix_and_outro_and_destroy_block(block, lookup) {
        block.f();
        outro_and_destroy_block(block, lookup);
    }
    function update_keyed_each(old_blocks, dirty, get_key, dynamic, ctx, list, lookup, node, destroy, create_each_block, next, get_context) {
        let o = old_blocks.length;
        let n = list.length;
        let i = o;
        const old_indexes = {};
        while (i--)
            old_indexes[old_blocks[i].key] = i;
        const new_blocks = [];
        const new_lookup = new Map();
        const deltas = new Map();
        i = n;
        while (i--) {
            const child_ctx = get_context(ctx, list, i);
            const key = get_key(child_ctx);
            let block = lookup.get(key);
            if (!block) {
                block = create_each_block(key, child_ctx);
                block.c();
            }
            else if (dynamic) {
                block.p(child_ctx, dirty);
            }
            new_lookup.set(key, new_blocks[i] = block);
            if (key in old_indexes)
                deltas.set(key, Math.abs(i - old_indexes[key]));
        }
        const will_move = new Set();
        const did_move = new Set();
        function insert(block) {
            transition_in(block, 1);
            block.m(node, next);
            lookup.set(block.key, block);
            next = block.first;
            n--;
        }
        while (o && n) {
            const new_block = new_blocks[n - 1];
            const old_block = old_blocks[o - 1];
            const new_key = new_block.key;
            const old_key = old_block.key;
            if (new_block === old_block) {
                // do nothing
                next = new_block.first;
                o--;
                n--;
            }
            else if (!new_lookup.has(old_key)) {
                // remove old block
                destroy(old_block, lookup);
                o--;
            }
            else if (!lookup.has(new_key) || will_move.has(new_key)) {
                insert(new_block);
            }
            else if (did_move.has(old_key)) {
                o--;
            }
            else if (deltas.get(new_key) > deltas.get(old_key)) {
                did_move.add(new_key);
                insert(new_block);
            }
            else {
                will_move.add(old_key);
                o--;
            }
        }
        while (o--) {
            const old_block = old_blocks[o];
            if (!new_lookup.has(old_block.key))
                destroy(old_block, lookup);
        }
        while (n)
            insert(new_blocks[n - 1]);
        return new_blocks;
    }
    function validate_each_keys(ctx, list, get_context, get_key) {
        const keys = new Set();
        for (let i = 0; i < list.length; i++) {
            const key = get_key(get_context(ctx, list, i));
            if (keys.has(key)) {
                throw new Error(`Cannot have duplicate keys in a keyed each`);
            }
            keys.add(key);
        }
    }

    function get_spread_update(levels, updates) {
        const update = {};
        const to_null_out = {};
        const accounted_for = { $$scope: 1 };
        let i = levels.length;
        while (i--) {
            const o = levels[i];
            const n = updates[i];
            if (n) {
                for (const key in o) {
                    if (!(key in n))
                        to_null_out[key] = 1;
                }
                for (const key in n) {
                    if (!accounted_for[key]) {
                        update[key] = n[key];
                        accounted_for[key] = 1;
                    }
                }
                levels[i] = n;
            }
            else {
                for (const key in o) {
                    accounted_for[key] = 1;
                }
            }
        }
        for (const key in to_null_out) {
            if (!(key in update))
                update[key] = undefined;
        }
        return update;
    }
    function get_spread_object(spread_props) {
        return typeof spread_props === 'object' && spread_props !== null ? spread_props : {};
    }

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

    function cubicOut(t) {
        const f = t - 1.0;
        return f * f * f + 1.0;
    }

    function fade(node, { delay = 0, duration = 400, easing = identity }) {
        const o = +getComputedStyle(node).opacity;
        return {
            delay,
            duration,
            easing,
            css: t => `opacity: ${t * o}`
        };
    }
    function fly(node, { delay = 0, duration = 400, easing = cubicOut, x = 0, y = 0, opacity = 0 }) {
        const style = getComputedStyle(node);
        const target_opacity = +style.opacity;
        const transform = style.transform === 'none' ? '' : style.transform;
        const od = target_opacity * (1 - opacity);
        return {
            delay,
            duration,
            easing,
            css: (t, u) => `
			transform: ${transform} translate(${(1 - t) * x}px, ${(1 - t) * y}px);
			opacity: ${target_opacity - (od * u)}`
        };
    }

    function flip(node, animation, params) {
        const style = getComputedStyle(node);
        const transform = style.transform === 'none' ? '' : style.transform;
        const scaleX = animation.from.width / node.clientWidth;
        const scaleY = animation.from.height / node.clientHeight;
        const dx = (animation.from.left - animation.to.left) / scaleX;
        const dy = (animation.from.top - animation.to.top) / scaleY;
        const d = Math.sqrt(dx * dx + dy * dy);
        const { delay = 0, duration = (d) => Math.sqrt(d) * 120, easing = cubicOut } = params;
        return {
            delay,
            duration: is_function(duration) ? duration(d) : duration,
            easing,
            css: (_t, u) => `transform: ${transform} translate(${u * dx}px, ${u * dy}px);`
        };
    }

    const subscriber_queue = [];
    /**
     * Creates a `Readable` store that allows reading by subscription.
     * @param value initial value
     * @param {StartStopNotifier}start start and stop notifications for subscriptions
     */
    function readable(value, start) {
        return {
            subscribe: writable(value, start).subscribe,
        };
    }
    /**
     * Create a `Writable` store that allows both updating and reading by subscription.
     * @param {*=}value initial value
     * @param {StartStopNotifier=}start start and stop notifications for subscriptions
     */
    function writable(value, start = noop) {
        let stop;
        const subscribers = [];
        function set(new_value) {
            if (safe_not_equal(value, new_value)) {
                value = new_value;
                if (stop) { // store is ready
                    const run_queue = !subscriber_queue.length;
                    for (let i = 0; i < subscribers.length; i += 1) {
                        const s = subscribers[i];
                        s[1]();
                        subscriber_queue.push(s, value);
                    }
                    if (run_queue) {
                        for (let i = 0; i < subscriber_queue.length; i += 2) {
                            subscriber_queue[i][0](subscriber_queue[i + 1]);
                        }
                        subscriber_queue.length = 0;
                    }
                }
            }
        }
        function update(fn) {
            set(fn(value));
        }
        function subscribe(run, invalidate = noop) {
            const subscriber = [run, invalidate];
            subscribers.push(subscriber);
            if (subscribers.length === 1) {
                stop = start(set) || noop;
            }
            run(value);
            return () => {
                const index = subscribers.indexOf(subscriber);
                if (index !== -1) {
                    subscribers.splice(index, 1);
                }
                if (subscribers.length === 0) {
                    stop();
                    stop = null;
                }
            };
        }
        return { set, update, subscribe };
    }
    function derived(stores, fn, initial_value) {
        const single = !Array.isArray(stores);
        const stores_array = single
            ? [stores]
            : stores;
        const auto = fn.length < 2;
        return readable(initial_value, (set) => {
            let inited = false;
            const values = [];
            let pending = 0;
            let cleanup = noop;
            const sync = () => {
                if (pending) {
                    return;
                }
                cleanup();
                const result = fn(single ? values[0] : values, set);
                if (auto) {
                    set(result);
                }
                else {
                    cleanup = is_function(result) ? result : noop;
                }
            };
            const unsubscribers = stores_array.map((store, i) => subscribe(store, (value) => {
                values[i] = value;
                pending &= ~(1 << i);
                if (inited) {
                    sync();
                }
            }, () => {
                pending |= (1 << i);
            }));
            inited = true;
            sync();
            return function stop() {
                run_all(unsubscribers);
                cleanup();
            };
        });
    }

    const createToast = () => {
      const { subscribe, update } = writable([]);
      let count = 0;
      let defaults = {};
      const push = (msg, opts = {}) => {
        const entry = { id: ++count, msg: msg, ...defaults, ...opts, theme: { ...defaults.theme, ...opts.theme } };
        update(n => entry.reversed ? [...n, entry] : [entry, ...n]);
        return count
      };
      const pop = id => {
        update(n => id ? n.filter(i => i.id !== id) : n.splice(1));
      };
      const set = (id, obj) => {
        update(n => {
          const idx = n.findIndex(i => i.id === id);
          if (idx > -1) {
            n[idx] = { ...n[idx], ...obj };
          }
          return n
        });
      };
      const _opts = (obj = {}) => {
        defaults = { ...defaults, ...obj, theme: { ...defaults.theme, ...obj.theme } };
        return defaults
      };
      return { subscribe, push, pop, set, _opts }
    };

    const toast = createToast();

    function is_date(obj) {
        return Object.prototype.toString.call(obj) === '[object Date]';
    }

    function get_interpolator(a, b) {
        if (a === b || a !== a)
            return () => a;
        const type = typeof a;
        if (type !== typeof b || Array.isArray(a) !== Array.isArray(b)) {
            throw new Error('Cannot interpolate values of different type');
        }
        if (Array.isArray(a)) {
            const arr = b.map((bi, i) => {
                return get_interpolator(a[i], bi);
            });
            return t => arr.map(fn => fn(t));
        }
        if (type === 'object') {
            if (!a || !b)
                throw new Error('Object cannot be null');
            if (is_date(a) && is_date(b)) {
                a = a.getTime();
                b = b.getTime();
                const delta = b - a;
                return t => new Date(a + t * delta);
            }
            const keys = Object.keys(b);
            const interpolators = {};
            keys.forEach(key => {
                interpolators[key] = get_interpolator(a[key], b[key]);
            });
            return t => {
                const result = {};
                keys.forEach(key => {
                    result[key] = interpolators[key](t);
                });
                return result;
            };
        }
        if (type === 'number') {
            const delta = b - a;
            return t => a + t * delta;
        }
        throw new Error(`Cannot interpolate ${type} values`);
    }
    function tweened(value, defaults = {}) {
        const store = writable(value);
        let task;
        let target_value = value;
        function set(new_value, opts) {
            if (value == null) {
                store.set(value = new_value);
                return Promise.resolve();
            }
            target_value = new_value;
            let previous_task = task;
            let started = false;
            let { delay = 0, duration = 400, easing = identity, interpolate = get_interpolator } = assign(assign({}, defaults), opts);
            if (duration === 0) {
                if (previous_task) {
                    previous_task.abort();
                    previous_task = null;
                }
                store.set(value = target_value);
                return Promise.resolve();
            }
            const start = now() + delay;
            let fn;
            task = loop(now => {
                if (now < start)
                    return true;
                if (!started) {
                    fn = interpolate(value, new_value);
                    if (typeof duration === 'function')
                        duration = duration(value, new_value);
                    started = true;
                }
                if (previous_task) {
                    previous_task.abort();
                    previous_task = null;
                }
                const elapsed = now - start;
                if (elapsed > duration) {
                    store.set(value = new_value);
                    return false;
                }
                // @ts-ignore
                store.set(value = fn(easing(elapsed / duration)));
                return true;
            });
            return task.promise;
        }
        return {
            set,
            update: (fn, opts) => set(fn(target_value, value), opts),
            subscribe: store.subscribe
        };
    }

    /* node_modules/@zerodevx/svelte-toast/src/ToastItem.svelte generated by Svelte v3.24.1 */
    const file = "node_modules/@zerodevx/svelte-toast/src/ToastItem.svelte";

    // (80:2) {#if item.dismissable}
    function create_if_block(ctx) {
    	let div;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			div = element("div");
    			div.textContent = "✕";
    			attr_dev(div, "class", "_toastBtn svelte-vfz6wa");
    			attr_dev(div, "role", "button");
    			attr_dev(div, "tabindex", "-1");
    			add_location(div, file, 80, 2, 1871);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);

    			if (!mounted) {
    				dispose = listen_dev(div, "click", /*click_handler*/ ctx[3], false, false, false);
    				mounted = true;
    			}
    		},
    		p: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block.name,
    		type: "if",
    		source: "(80:2) {#if item.dismissable}",
    		ctx
    	});

    	return block;
    }

    function create_fragment(ctx) {
    	let div1;
    	let div0;
    	let t0_value = /*item*/ ctx[0].msg + "";
    	let t0;
    	let t1;
    	let t2;
    	let progress_1;
    	let if_block = /*item*/ ctx[0].dismissable && create_if_block(ctx);

    	const block = {
    		c: function create() {
    			div1 = element("div");
    			div0 = element("div");
    			t0 = text(t0_value);
    			t1 = space();
    			if (if_block) if_block.c();
    			t2 = space();
    			progress_1 = element("progress");
    			attr_dev(div0, "class", "_toastMsg svelte-vfz6wa");
    			add_location(div0, file, 77, 2, 1803);
    			attr_dev(progress_1, "class", "_toastBar svelte-vfz6wa");
    			progress_1.value = /*$progress*/ ctx[1];
    			add_location(progress_1, file, 83, 2, 1977);
    			attr_dev(div1, "class", "_toastItem svelte-vfz6wa");
    			add_location(div1, file, 76, 0, 1776);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div1, anchor);
    			append_dev(div1, div0);
    			append_dev(div0, t0);
    			append_dev(div1, t1);
    			if (if_block) if_block.m(div1, null);
    			append_dev(div1, t2);
    			append_dev(div1, progress_1);
    		},
    		p: function update(ctx, [dirty]) {
    			if (dirty & /*item*/ 1 && t0_value !== (t0_value = /*item*/ ctx[0].msg + "")) set_data_dev(t0, t0_value);

    			if (/*item*/ ctx[0].dismissable) {
    				if (if_block) {
    					if_block.p(ctx, dirty);
    				} else {
    					if_block = create_if_block(ctx);
    					if_block.c();
    					if_block.m(div1, t2);
    				}
    			} else if (if_block) {
    				if_block.d(1);
    				if_block = null;
    			}

    			if (dirty & /*$progress*/ 2) {
    				prop_dev(progress_1, "value", /*$progress*/ ctx[1]);
    			}
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div1);
    			if (if_block) if_block.d();
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
    	let $progress;
    	let { item } = $$props;
    	const progress = tweened(item.initial, { duration: item.duration, easing: identity });
    	validate_store(progress, "progress");
    	component_subscribe($$self, progress, value => $$invalidate(1, $progress = value));
    	let prevProgress = item.initial;
    	const writable_props = ["item"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<ToastItem> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("ToastItem", $$slots, []);
    	const click_handler = () => toast.pop(item.id);

    	$$self.$$set = $$props => {
    		if ("item" in $$props) $$invalidate(0, item = $$props.item);
    	};

    	$$self.$capture_state = () => ({
    		tweened,
    		linear: identity,
    		toast,
    		item,
    		progress,
    		prevProgress,
    		$progress
    	});

    	$$self.$inject_state = $$props => {
    		if ("item" in $$props) $$invalidate(0, item = $$props.item);
    		if ("prevProgress" in $$props) $$invalidate(4, prevProgress = $$props.prevProgress);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*prevProgress, item*/ 17) {
    			 if (prevProgress !== item.progress) {
    				if (item.progress === 1 || item.progress === 0) {
    					progress.set(item.progress).then(() => toast.pop(item.id));
    				} else {
    					progress.set(item.progress);
    				}

    				$$invalidate(4, prevProgress = item.progress);
    			}
    		}
    	};

    	return [item, $progress, progress, click_handler];
    }

    class ToastItem extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance, create_fragment, safe_not_equal, { item: 0 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "ToastItem",
    			options,
    			id: create_fragment.name
    		});

    		const { ctx } = this.$$;
    		const props = options.props || {};

    		if (/*item*/ ctx[0] === undefined && !("item" in props)) {
    			console.warn("<ToastItem> was created without expected prop 'item'");
    		}
    	}

    	get item() {
    		throw new Error("<ToastItem>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set item(value) {
    		throw new Error("<ToastItem>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* node_modules/@zerodevx/svelte-toast/src/SvelteToast.svelte generated by Svelte v3.24.1 */

    const { Object: Object_1 } = globals;
    const file$1 = "node_modules/@zerodevx/svelte-toast/src/SvelteToast.svelte";

    function get_each_context(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[4] = list[i];
    	return child_ctx;
    }

    // (39:2) {#each $toast as item (item.id)}
    function create_each_block(key_1, ctx) {
    	let li;
    	let toastitem;
    	let t;
    	let li_style_value;
    	let li_intro;
    	let li_outro;
    	let rect;
    	let stop_animation = noop;
    	let current;

    	toastitem = new ToastItem({
    			props: { item: /*item*/ ctx[4] },
    			$$inline: true
    		});

    	const block = {
    		key: key_1,
    		first: null,
    		c: function create() {
    			li = element("li");
    			create_component(toastitem.$$.fragment);
    			t = space();
    			attr_dev(li, "style", li_style_value = /*getCss*/ ctx[1](/*item*/ ctx[4].theme));
    			add_location(li, file$1, 39, 2, 830);
    			this.first = li;
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, li, anchor);
    			mount_component(toastitem, li, null);
    			append_dev(li, t);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			const toastitem_changes = {};
    			if (dirty & /*$toast*/ 1) toastitem_changes.item = /*item*/ ctx[4];
    			toastitem.$set(toastitem_changes);

    			if (!current || dirty & /*$toast*/ 1 && li_style_value !== (li_style_value = /*getCss*/ ctx[1](/*item*/ ctx[4].theme))) {
    				attr_dev(li, "style", li_style_value);
    			}
    		},
    		r: function measure() {
    			rect = li.getBoundingClientRect();
    		},
    		f: function fix() {
    			fix_position(li);
    			stop_animation();
    			add_transform(li, rect);
    		},
    		a: function animate() {
    			stop_animation();
    			stop_animation = create_animation(li, rect, flip, { duration: 200 });
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(toastitem.$$.fragment, local);

    			add_render_callback(() => {
    				if (li_outro) li_outro.end(1);
    				if (!li_intro) li_intro = create_in_transition(li, fly, /*item*/ ctx[4].intro);
    				li_intro.start();
    			});

    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(toastitem.$$.fragment, local);
    			if (li_intro) li_intro.invalidate();
    			li_outro = create_out_transition(li, fade, {});
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(li);
    			destroy_component(toastitem);
    			if (detaching && li_outro) li_outro.end();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block.name,
    		type: "each",
    		source: "(39:2) {#each $toast as item (item.id)}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$1(ctx) {
    	let ul;
    	let each_blocks = [];
    	let each_1_lookup = new Map();
    	let current;
    	let each_value = /*$toast*/ ctx[0];
    	validate_each_argument(each_value);
    	const get_key = ctx => /*item*/ ctx[4].id;
    	validate_each_keys(ctx, each_value, get_each_context, get_key);

    	for (let i = 0; i < each_value.length; i += 1) {
    		let child_ctx = get_each_context(ctx, each_value, i);
    		let key = get_key(child_ctx);
    		each_1_lookup.set(key, each_blocks[i] = create_each_block(key, child_ctx));
    	}

    	const block = {
    		c: function create() {
    			ul = element("ul");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			attr_dev(ul, "class", "svelte-ivwmun");
    			add_location(ul, file$1, 37, 0, 788);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, ul, anchor);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(ul, null);
    			}

    			current = true;
    		},
    		p: function update(ctx, [dirty]) {
    			if (dirty & /*getCss, $toast*/ 3) {
    				const each_value = /*$toast*/ ctx[0];
    				validate_each_argument(each_value);
    				group_outros();
    				for (let i = 0; i < each_blocks.length; i += 1) each_blocks[i].r();
    				validate_each_keys(ctx, each_value, get_each_context, get_key);
    				each_blocks = update_keyed_each(each_blocks, dirty, get_key, 1, ctx, each_value, each_1_lookup, ul, fix_and_outro_and_destroy_block, create_each_block, null, get_each_context);
    				for (let i = 0; i < each_blocks.length; i += 1) each_blocks[i].a();
    				check_outros();
    			}
    		},
    		i: function intro(local) {
    			if (current) return;

    			for (let i = 0; i < each_value.length; i += 1) {
    				transition_in(each_blocks[i]);
    			}

    			current = true;
    		},
    		o: function outro(local) {
    			for (let i = 0; i < each_blocks.length; i += 1) {
    				transition_out(each_blocks[i]);
    			}

    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(ul);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].d();
    			}
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

    function instance$1($$self, $$props, $$invalidate) {
    	let $toast;
    	validate_store(toast, "toast");
    	component_subscribe($$self, toast, $$value => $$invalidate(0, $toast = $$value));
    	let { options = {} } = $$props;

    	const defaults = {
    		duration: 4000,
    		dismissable: true,
    		initial: 1,
    		progress: 0,
    		reversed: false,
    		intro: { x: 256 },
    		theme: {}
    	};

    	toast._opts(defaults);
    	const getCss = theme => Object.keys(theme).reduce((a, c) => `${a}${c}:${theme[c]};`, "");
    	const writable_props = ["options"];

    	Object_1.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<SvelteToast> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("SvelteToast", $$slots, []);

    	$$self.$$set = $$props => {
    		if ("options" in $$props) $$invalidate(2, options = $$props.options);
    	};

    	$$self.$capture_state = () => ({
    		fade,
    		fly,
    		flip,
    		toast,
    		ToastItem,
    		options,
    		defaults,
    		getCss,
    		$toast
    	});

    	$$self.$inject_state = $$props => {
    		if ("options" in $$props) $$invalidate(2, options = $$props.options);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*options*/ 4) {
    			 toast._opts(options);
    		}
    	};

    	return [$toast, getCss, options];
    }

    class SvelteToast extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$1, create_fragment$1, safe_not_equal, { options: 2 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "SvelteToast",
    			options,
    			id: create_fragment$1.name
    		});
    	}

    	get options() {
    		throw new Error("<SvelteToast>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set options(value) {
    		throw new Error("<SvelteToast>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /**
     * @typedef {Object} WrappedComponent Object returned by the `wrap` method
     * @property {SvelteComponent} component - Component to load (this is always asynchronous)
     * @property {RoutePrecondition[]} [conditions] - Route pre-conditions to validate
     * @property {Object} [props] - Optional dictionary of static props
     * @property {Object} [userData] - Optional user data dictionary
     * @property {bool} _sveltesparouter - Internal flag; always set to true
     */

    /**
     * @callback AsyncSvelteComponent
     * @returns {Promise<SvelteComponent>} Returns a Promise that resolves with a Svelte component
     */

    /**
     * @callback RoutePrecondition
     * @param {RouteDetail} detail - Route detail object
     * @returns {boolean|Promise<boolean>} If the callback returns a false-y value, it's interpreted as the precondition failed, so it aborts loading the component (and won't process other pre-condition callbacks)
     */

    /**
     * @typedef {Object} WrapOptions Options object for the call to `wrap`
     * @property {SvelteComponent} [component] - Svelte component to load (this is incompatible with `asyncComponent`)
     * @property {AsyncSvelteComponent} [asyncComponent] - Function that returns a Promise that fulfills with a Svelte component (e.g. `{asyncComponent: () => import('Foo.svelte')}`)
     * @property {SvelteComponent} [loadingComponent] - Svelte component to be displayed while the async route is loading (as a placeholder); when unset or false-y, no component is shown while component
     * @property {object} [loadingParams] - Optional dictionary passed to the `loadingComponent` component as params (for an exported prop called `params`)
     * @property {object} [userData] - Optional object that will be passed to events such as `routeLoading`, `routeLoaded`, `conditionsFailed`
     * @property {object} [props] - Optional key-value dictionary of static props that will be passed to the component. The props are expanded with {...props}, so the key in the dictionary becomes the name of the prop.
     * @property {RoutePrecondition[]|RoutePrecondition} [conditions] - Route pre-conditions to add, which will be executed in order
     */

    /**
     * Wraps a component to enable multiple capabilities:
     * 1. Using dynamically-imported component, with (e.g. `{asyncComponent: () => import('Foo.svelte')}`), which also allows bundlers to do code-splitting.
     * 2. Adding route pre-conditions (e.g. `{conditions: [...]}`)
     * 3. Adding static props that are passed to the component
     * 4. Adding custom userData, which is passed to route events (e.g. route loaded events) or to route pre-conditions (e.g. `{userData: {foo: 'bar}}`)
     * 
     * @param {WrapOptions} args - Arguments object
     * @returns {WrappedComponent} Wrapped component
     */
    function wrap(args) {
        if (!args) {
            throw Error('Parameter args is required')
        }

        // We need to have one and only one of component and asyncComponent
        // This does a "XNOR"
        if (!args.component == !args.asyncComponent) {
            throw Error('One and only one of component and asyncComponent is required')
        }

        // If the component is not async, wrap it into a function returning a Promise
        if (args.component) {
            args.asyncComponent = () => Promise.resolve(args.component);
        }

        // Parameter asyncComponent and each item of conditions must be functions
        if (typeof args.asyncComponent != 'function') {
            throw Error('Parameter asyncComponent must be a function')
        }
        if (args.conditions) {
            // Ensure it's an array
            if (!Array.isArray(args.conditions)) {
                args.conditions = [args.conditions];
            }
            for (let i = 0; i < args.conditions.length; i++) {
                if (!args.conditions[i] || typeof args.conditions[i] != 'function') {
                    throw Error('Invalid parameter conditions[' + i + ']')
                }
            }
        }

        // Check if we have a placeholder component
        if (args.loadingComponent) {
            args.asyncComponent.loading = args.loadingComponent;
            args.asyncComponent.loadingParams = args.loadingParams || undefined;
        }

        // Returns an object that contains all the functions to execute too
        // The _sveltesparouter flag is to confirm the object was created by this router
        const obj = {
            component: args.asyncComponent,
            userData: args.userData,
            conditions: (args.conditions && args.conditions.length) ? args.conditions : undefined,
            props: (args.props && Object.keys(args.props).length) ? args.props : {},
            _sveltesparouter: true
        };

        return obj
    }

    function regexparam (str, loose) {
    	if (str instanceof RegExp) return { keys:false, pattern:str };
    	var c, o, tmp, ext, keys=[], pattern='', arr = str.split('/');
    	arr[0] || arr.shift();

    	while (tmp = arr.shift()) {
    		c = tmp[0];
    		if (c === '*') {
    			keys.push('wild');
    			pattern += '/(.*)';
    		} else if (c === ':') {
    			o = tmp.indexOf('?', 1);
    			ext = tmp.indexOf('.', 1);
    			keys.push( tmp.substring(1, !!~o ? o : !!~ext ? ext : tmp.length) );
    			pattern += !!~o && !~ext ? '(?:/([^/]+?))?' : '/([^/]+?)';
    			if (!!~ext) pattern += (!!~o ? '?' : '') + '\\' + tmp.substring(ext);
    		} else {
    			pattern += '/' + tmp;
    		}
    	}

    	return {
    		keys: keys,
    		pattern: new RegExp('^' + pattern + (loose ? '(?=$|\/)' : '\/?$'), 'i')
    	};
    }

    /* node_modules/svelte-spa-router/Router.svelte generated by Svelte v3.24.1 */

    const { Error: Error_1, Object: Object_1$1, console: console_1 } = globals;

    // (209:0) {:else}
    function create_else_block(ctx) {
    	let switch_instance;
    	let switch_instance_anchor;
    	let current;
    	const switch_instance_spread_levels = [/*props*/ ctx[2]];
    	var switch_value = /*component*/ ctx[0];

    	function switch_props(ctx) {
    		let switch_instance_props = {};

    		for (let i = 0; i < switch_instance_spread_levels.length; i += 1) {
    			switch_instance_props = assign(switch_instance_props, switch_instance_spread_levels[i]);
    		}

    		return {
    			props: switch_instance_props,
    			$$inline: true
    		};
    	}

    	if (switch_value) {
    		switch_instance = new switch_value(switch_props());
    		switch_instance.$on("routeEvent", /*routeEvent_handler_1*/ ctx[7]);
    	}

    	const block = {
    		c: function create() {
    			if (switch_instance) create_component(switch_instance.$$.fragment);
    			switch_instance_anchor = empty();
    		},
    		m: function mount(target, anchor) {
    			if (switch_instance) {
    				mount_component(switch_instance, target, anchor);
    			}

    			insert_dev(target, switch_instance_anchor, anchor);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			const switch_instance_changes = (dirty & /*props*/ 4)
    			? get_spread_update(switch_instance_spread_levels, [get_spread_object(/*props*/ ctx[2])])
    			: {};

    			if (switch_value !== (switch_value = /*component*/ ctx[0])) {
    				if (switch_instance) {
    					group_outros();
    					const old_component = switch_instance;

    					transition_out(old_component.$$.fragment, 1, 0, () => {
    						destroy_component(old_component, 1);
    					});

    					check_outros();
    				}

    				if (switch_value) {
    					switch_instance = new switch_value(switch_props());
    					switch_instance.$on("routeEvent", /*routeEvent_handler_1*/ ctx[7]);
    					create_component(switch_instance.$$.fragment);
    					transition_in(switch_instance.$$.fragment, 1);
    					mount_component(switch_instance, switch_instance_anchor.parentNode, switch_instance_anchor);
    				} else {
    					switch_instance = null;
    				}
    			} else if (switch_value) {
    				switch_instance.$set(switch_instance_changes);
    			}
    		},
    		i: function intro(local) {
    			if (current) return;
    			if (switch_instance) transition_in(switch_instance.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			if (switch_instance) transition_out(switch_instance.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(switch_instance_anchor);
    			if (switch_instance) destroy_component(switch_instance, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block.name,
    		type: "else",
    		source: "(209:0) {:else}",
    		ctx
    	});

    	return block;
    }

    // (202:0) {#if componentParams}
    function create_if_block$1(ctx) {
    	let switch_instance;
    	let switch_instance_anchor;
    	let current;
    	const switch_instance_spread_levels = [{ params: /*componentParams*/ ctx[1] }, /*props*/ ctx[2]];
    	var switch_value = /*component*/ ctx[0];

    	function switch_props(ctx) {
    		let switch_instance_props = {};

    		for (let i = 0; i < switch_instance_spread_levels.length; i += 1) {
    			switch_instance_props = assign(switch_instance_props, switch_instance_spread_levels[i]);
    		}

    		return {
    			props: switch_instance_props,
    			$$inline: true
    		};
    	}

    	if (switch_value) {
    		switch_instance = new switch_value(switch_props());
    		switch_instance.$on("routeEvent", /*routeEvent_handler*/ ctx[6]);
    	}

    	const block = {
    		c: function create() {
    			if (switch_instance) create_component(switch_instance.$$.fragment);
    			switch_instance_anchor = empty();
    		},
    		m: function mount(target, anchor) {
    			if (switch_instance) {
    				mount_component(switch_instance, target, anchor);
    			}

    			insert_dev(target, switch_instance_anchor, anchor);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			const switch_instance_changes = (dirty & /*componentParams, props*/ 6)
    			? get_spread_update(switch_instance_spread_levels, [
    					dirty & /*componentParams*/ 2 && { params: /*componentParams*/ ctx[1] },
    					dirty & /*props*/ 4 && get_spread_object(/*props*/ ctx[2])
    				])
    			: {};

    			if (switch_value !== (switch_value = /*component*/ ctx[0])) {
    				if (switch_instance) {
    					group_outros();
    					const old_component = switch_instance;

    					transition_out(old_component.$$.fragment, 1, 0, () => {
    						destroy_component(old_component, 1);
    					});

    					check_outros();
    				}

    				if (switch_value) {
    					switch_instance = new switch_value(switch_props());
    					switch_instance.$on("routeEvent", /*routeEvent_handler*/ ctx[6]);
    					create_component(switch_instance.$$.fragment);
    					transition_in(switch_instance.$$.fragment, 1);
    					mount_component(switch_instance, switch_instance_anchor.parentNode, switch_instance_anchor);
    				} else {
    					switch_instance = null;
    				}
    			} else if (switch_value) {
    				switch_instance.$set(switch_instance_changes);
    			}
    		},
    		i: function intro(local) {
    			if (current) return;
    			if (switch_instance) transition_in(switch_instance.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			if (switch_instance) transition_out(switch_instance.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(switch_instance_anchor);
    			if (switch_instance) destroy_component(switch_instance, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$1.name,
    		type: "if",
    		source: "(202:0) {#if componentParams}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$2(ctx) {
    	let current_block_type_index;
    	let if_block;
    	let if_block_anchor;
    	let current;
    	const if_block_creators = [create_if_block$1, create_else_block];
    	const if_blocks = [];

    	function select_block_type(ctx, dirty) {
    		if (/*componentParams*/ ctx[1]) return 0;
    		return 1;
    	}

    	current_block_type_index = select_block_type(ctx);
    	if_block = if_blocks[current_block_type_index] = if_block_creators[current_block_type_index](ctx);

    	const block = {
    		c: function create() {
    			if_block.c();
    			if_block_anchor = empty();
    		},
    		l: function claim(nodes) {
    			throw new Error_1("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			if_blocks[current_block_type_index].m(target, anchor);
    			insert_dev(target, if_block_anchor, anchor);
    			current = true;
    		},
    		p: function update(ctx, [dirty]) {
    			let previous_block_index = current_block_type_index;
    			current_block_type_index = select_block_type(ctx);

    			if (current_block_type_index === previous_block_index) {
    				if_blocks[current_block_type_index].p(ctx, dirty);
    			} else {
    				group_outros();

    				transition_out(if_blocks[previous_block_index], 1, 1, () => {
    					if_blocks[previous_block_index] = null;
    				});

    				check_outros();
    				if_block = if_blocks[current_block_type_index];

    				if (!if_block) {
    					if_block = if_blocks[current_block_type_index] = if_block_creators[current_block_type_index](ctx);
    					if_block.c();
    				}

    				transition_in(if_block, 1);
    				if_block.m(if_block_anchor.parentNode, if_block_anchor);
    			}
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(if_block);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(if_block);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if_blocks[current_block_type_index].d(detaching);
    			if (detaching) detach_dev(if_block_anchor);
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

    function wrap$1(component, userData, ...conditions) {
    	// Use the new wrap method and show a deprecation warning
    	// eslint-disable-next-line no-console
    	console.warn("Method `wrap` from `svelte-spa-router` is deprecated and will be removed in a future version. Please use `svelte-spa-router/wrap` instead. See http://bit.ly/svelte-spa-router-upgrading");

    	return wrap({ component, userData, conditions });
    }

    /**
     * @typedef {Object} Location
     * @property {string} location - Location (page/view), for example `/book`
     * @property {string} [querystring] - Querystring from the hash, as a string not parsed
     */
    /**
     * Returns the current location from the hash.
     *
     * @returns {Location} Location object
     * @private
     */
    function getLocation() {
    	const hashPosition = window.location.href.indexOf("#/");

    	let location = hashPosition > -1
    	? window.location.href.substr(hashPosition + 1)
    	: "/";

    	// Check if there's a querystring
    	const qsPosition = location.indexOf("?");

    	let querystring = "";

    	if (qsPosition > -1) {
    		querystring = location.substr(qsPosition + 1);
    		location = location.substr(0, qsPosition);
    	}

    	return { location, querystring };
    }

    const loc = readable(null, // eslint-disable-next-line prefer-arrow-callback
    function start(set) {
    	set(getLocation());

    	const update = () => {
    		set(getLocation());
    	};

    	window.addEventListener("hashchange", update, false);

    	return function stop() {
    		window.removeEventListener("hashchange", update, false);
    	};
    });

    const location = derived(loc, $loc => $loc.location);
    const querystring = derived(loc, $loc => $loc.querystring);

    async function push(location) {
    	if (!location || location.length < 1 || location.charAt(0) != "/" && location.indexOf("#/") !== 0) {
    		throw Error("Invalid parameter location");
    	}

    	// Execute this code when the current call stack is complete
    	await tick();

    	// Note: this will include scroll state in history even when restoreScrollState is false
    	history.replaceState(
    		{
    			scrollX: window.scrollX,
    			scrollY: window.scrollY
    		},
    		undefined,
    		undefined
    	);

    	window.location.hash = (location.charAt(0) == "#" ? "" : "#") + location;
    }

    async function pop() {
    	// Execute this code when the current call stack is complete
    	await tick();

    	window.history.back();
    }

    async function replace(location) {
    	if (!location || location.length < 1 || location.charAt(0) != "/" && location.indexOf("#/") !== 0) {
    		throw Error("Invalid parameter location");
    	}

    	// Execute this code when the current call stack is complete
    	await tick();

    	const dest = (location.charAt(0) == "#" ? "" : "#") + location;

    	try {
    		window.history.replaceState(undefined, undefined, dest);
    	} catch(e) {
    		// eslint-disable-next-line no-console
    		console.warn("Caught exception while replacing the current page. If you're running this in the Svelte REPL, please note that the `replace` method might not work in this environment.");
    	}

    	// The method above doesn't trigger the hashchange event, so let's do that manually
    	window.dispatchEvent(new Event("hashchange"));
    }

    function link(node, hrefVar) {
    	// Only apply to <a> tags
    	if (!node || !node.tagName || node.tagName.toLowerCase() != "a") {
    		throw Error("Action \"link\" can only be used with <a> tags");
    	}

    	updateLink(node, hrefVar || node.getAttribute("href"));

    	return {
    		update(updated) {
    			updateLink(node, updated);
    		}
    	};
    }

    // Internal function used by the link function
    function updateLink(node, href) {
    	// Destination must start with '/'
    	if (!href || href.length < 1 || href.charAt(0) != "/") {
    		throw Error("Invalid value for \"href\" attribute: " + href);
    	}

    	// Add # to the href attribute
    	node.setAttribute("href", "#" + href);

    	node.addEventListener("click", scrollstateHistoryHandler);
    }

    /**
     * The handler attached to an anchor tag responsible for updating the
     * current history state with the current scroll state
     *
     * @param {HTMLElementEventMap} event - an onclick event attached to an anchor tag
     */
    function scrollstateHistoryHandler(event) {
    	// Prevent default anchor onclick behaviour
    	event.preventDefault();

    	const href = event.currentTarget.getAttribute("href");

    	// Setting the url (3rd arg) to href will break clicking for reasons, so don't try to do that
    	history.replaceState(
    		{
    			scrollX: window.scrollX,
    			scrollY: window.scrollY
    		},
    		undefined,
    		undefined
    	);

    	// This will force an update as desired, but this time our scroll state will be attached
    	window.location.hash = href;
    }

    function instance$2($$self, $$props, $$invalidate) {
    	let { routes = {} } = $$props;
    	let { prefix = "" } = $$props;
    	let { restoreScrollState = false } = $$props;

    	/**
     * Container for a route: path, component
     */
    	class RouteItem {
    		/**
     * Initializes the object and creates a regular expression from the path, using regexparam.
     *
     * @param {string} path - Path to the route (must start with '/' or '*')
     * @param {SvelteComponent|WrappedComponent} component - Svelte component for the route, optionally wrapped
     */
    		constructor(path, component) {
    			if (!component || typeof component != "function" && (typeof component != "object" || component._sveltesparouter !== true)) {
    				throw Error("Invalid component object");
    			}

    			// Path must be a regular or expression, or a string starting with '/' or '*'
    			if (!path || typeof path == "string" && (path.length < 1 || path.charAt(0) != "/" && path.charAt(0) != "*") || typeof path == "object" && !(path instanceof RegExp)) {
    				throw Error("Invalid value for \"path\" argument - strings must start with / or *");
    			}

    			const { pattern, keys } = regexparam(path);
    			this.path = path;

    			// Check if the component is wrapped and we have conditions
    			if (typeof component == "object" && component._sveltesparouter === true) {
    				this.component = component.component;
    				this.conditions = component.conditions || [];
    				this.userData = component.userData;
    				this.props = component.props || {};
    			} else {
    				// Convert the component to a function that returns a Promise, to normalize it
    				this.component = () => Promise.resolve(component);

    				this.conditions = [];
    				this.props = {};
    			}

    			this._pattern = pattern;
    			this._keys = keys;
    		}

    		/**
     * Checks if `path` matches the current route.
     * If there's a match, will return the list of parameters from the URL (if any).
     * In case of no match, the method will return `null`.
     *
     * @param {string} path - Path to test
     * @returns {null|Object.<string, string>} List of paramters from the URL if there's a match, or `null` otherwise.
     */
    		match(path) {
    			// If there's a prefix, check if it matches the start of the path.
    			// If not, bail early, else remove it before we run the matching.
    			if (prefix) {
    				if (typeof prefix == "string") {
    					if (path.startsWith(prefix)) {
    						path = path.substr(prefix.length) || "/";
    					} else {
    						return null;
    					}
    				} else if (prefix instanceof RegExp) {
    					const match = path.match(prefix);

    					if (match && match[0]) {
    						path = path.substr(match[0].length) || "/";
    					} else {
    						return null;
    					}
    				}
    			}

    			// Check if the pattern matches
    			const matches = this._pattern.exec(path);

    			if (matches === null) {
    				return null;
    			}

    			// If the input was a regular expression, this._keys would be false, so return matches as is
    			if (this._keys === false) {
    				return matches;
    			}

    			const out = {};
    			let i = 0;

    			while (i < this._keys.length) {
    				// In the match parameters, URL-decode all values
    				try {
    					out[this._keys[i]] = decodeURIComponent(matches[i + 1] || "") || null;
    				} catch(e) {
    					out[this._keys[i]] = null;
    				}

    				i++;
    			}

    			return out;
    		}

    		/**
     * Dictionary with route details passed to the pre-conditions functions, as well as the `routeLoading`, `routeLoaded` and `conditionsFailed` events
     * @typedef {Object} RouteDetail
     * @property {string|RegExp} route - Route matched as defined in the route definition (could be a string or a reguar expression object)
     * @property {string} location - Location path
     * @property {string} querystring - Querystring from the hash
     * @property {object} [userData] - Custom data passed by the user
     * @property {SvelteComponent} [component] - Svelte component (only in `routeLoaded` events)
     * @property {string} [name] - Name of the Svelte component (only in `routeLoaded` events)
     */
    		/**
     * Executes all conditions (if any) to control whether the route can be shown. Conditions are executed in the order they are defined, and if a condition fails, the following ones aren't executed.
     * 
     * @param {RouteDetail} detail - Route detail
     * @returns {bool} Returns true if all the conditions succeeded
     */
    		async checkConditions(detail) {
    			for (let i = 0; i < this.conditions.length; i++) {
    				if (!await this.conditions[i](detail)) {
    					return false;
    				}
    			}

    			return true;
    		}
    	}

    	// Set up all routes
    	const routesList = [];

    	if (routes instanceof Map) {
    		// If it's a map, iterate on it right away
    		routes.forEach((route, path) => {
    			routesList.push(new RouteItem(path, route));
    		});
    	} else {
    		// We have an object, so iterate on its own properties
    		Object.keys(routes).forEach(path => {
    			routesList.push(new RouteItem(path, routes[path]));
    		});
    	}

    	// Props for the component to render
    	let component = null;

    	let componentParams = null;
    	let props = {};

    	// Event dispatcher from Svelte
    	const dispatch = createEventDispatcher();

    	// Just like dispatch, but executes on the next iteration of the event loop
    	async function dispatchNextTick(name, detail) {
    		// Execute this code when the current call stack is complete
    		await tick();

    		dispatch(name, detail);
    	}

    	// If this is set, then that means we have popped into this var the state of our last scroll position
    	let previousScrollState = null;

    	if (restoreScrollState) {
    		window.addEventListener("popstate", event => {
    			// If this event was from our history.replaceState, event.state will contain
    			// our scroll history. Otherwise, event.state will be null (like on forward
    			// navigation)
    			if (event.state && event.state.scrollY) {
    				previousScrollState = event.state;
    			} else {
    				previousScrollState = null;
    			}
    		});

    		afterUpdate(() => {
    			// If this exists, then this is a back navigation: restore the scroll position
    			if (previousScrollState) {
    				window.scrollTo(previousScrollState.scrollX, previousScrollState.scrollY);
    			} else {
    				// Otherwise this is a forward navigation: scroll to top
    				window.scrollTo(0, 0);
    			}
    		});
    	}

    	// Always have the latest value of loc
    	let lastLoc = null;

    	// Current object of the component loaded
    	let componentObj = null;

    	// Handle hash change events
    	// Listen to changes in the $loc store and update the page
    	// Do not use the $: syntax because it gets triggered by too many things
    	loc.subscribe(async newLoc => {
    		lastLoc = newLoc;

    		// Find a route matching the location
    		let i = 0;

    		while (i < routesList.length) {
    			const match = routesList[i].match(newLoc.location);

    			if (!match) {
    				i++;
    				continue;
    			}

    			const detail = {
    				route: routesList[i].path,
    				location: newLoc.location,
    				querystring: newLoc.querystring,
    				userData: routesList[i].userData
    			};

    			// Check if the route can be loaded - if all conditions succeed
    			if (!await routesList[i].checkConditions(detail)) {
    				// Don't display anything
    				$$invalidate(0, component = null);

    				componentObj = null;

    				// Trigger an event to notify the user, then exit
    				dispatchNextTick("conditionsFailed", detail);

    				return;
    			}

    			// Trigger an event to alert that we're loading the route
    			// We need to clone the object on every event invocation so we don't risk the object to be modified in the next tick
    			dispatchNextTick("routeLoading", Object.assign({}, detail));

    			// If there's a component to show while we're loading the route, display it
    			const obj = routesList[i].component;

    			// Do not replace the component if we're loading the same one as before, to avoid the route being unmounted and re-mounted
    			if (componentObj != obj) {
    				if (obj.loading) {
    					$$invalidate(0, component = obj.loading);
    					componentObj = obj;
    					$$invalidate(1, componentParams = obj.loadingParams);
    					$$invalidate(2, props = {});

    					// Trigger the routeLoaded event for the loading component
    					// Create a copy of detail so we don't modify the object for the dynamic route (and the dynamic route doesn't modify our object too)
    					dispatchNextTick("routeLoaded", Object.assign({}, detail, { component, name: component.name }));
    				} else {
    					$$invalidate(0, component = null);
    					componentObj = null;
    				}

    				// Invoke the Promise
    				const loaded = await obj();

    				// Now that we're here, after the promise resolved, check if we still want this component, as the user might have navigated to another page in the meanwhile
    				if (newLoc != lastLoc) {
    					// Don't update the component, just exit
    					return;
    				}

    				// If there is a "default" property, which is used by async routes, then pick that
    				$$invalidate(0, component = loaded && loaded.default || loaded);

    				componentObj = obj;
    			}

    			// Set componentParams only if we have a match, to avoid a warning similar to `<Component> was created with unknown prop 'params'`
    			// Of course, this assumes that developers always add a "params" prop when they are expecting parameters
    			if (match && typeof match == "object" && Object.keys(match).length) {
    				$$invalidate(1, componentParams = match);
    			} else {
    				$$invalidate(1, componentParams = null);
    			}

    			// Set static props, if any
    			$$invalidate(2, props = routesList[i].props);

    			// Dispatch the routeLoaded event then exit
    			// We need to clone the object on every event invocation so we don't risk the object to be modified in the next tick
    			dispatchNextTick("routeLoaded", Object.assign({}, detail, { component, name: component.name }));

    			return;
    		}

    		// If we're still here, there was no match, so show the empty component
    		$$invalidate(0, component = null);

    		componentObj = null;
    	});

    	const writable_props = ["routes", "prefix", "restoreScrollState"];

    	Object_1$1.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console_1.warn(`<Router> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("Router", $$slots, []);

    	function routeEvent_handler(event) {
    		bubble($$self, event);
    	}

    	function routeEvent_handler_1(event) {
    		bubble($$self, event);
    	}

    	$$self.$$set = $$props => {
    		if ("routes" in $$props) $$invalidate(3, routes = $$props.routes);
    		if ("prefix" in $$props) $$invalidate(4, prefix = $$props.prefix);
    		if ("restoreScrollState" in $$props) $$invalidate(5, restoreScrollState = $$props.restoreScrollState);
    	};

    	$$self.$capture_state = () => ({
    		readable,
    		derived,
    		tick,
    		_wrap: wrap,
    		wrap: wrap$1,
    		getLocation,
    		loc,
    		location,
    		querystring,
    		push,
    		pop,
    		replace,
    		link,
    		updateLink,
    		scrollstateHistoryHandler,
    		createEventDispatcher,
    		afterUpdate,
    		regexparam,
    		routes,
    		prefix,
    		restoreScrollState,
    		RouteItem,
    		routesList,
    		component,
    		componentParams,
    		props,
    		dispatch,
    		dispatchNextTick,
    		previousScrollState,
    		lastLoc,
    		componentObj
    	});

    	$$self.$inject_state = $$props => {
    		if ("routes" in $$props) $$invalidate(3, routes = $$props.routes);
    		if ("prefix" in $$props) $$invalidate(4, prefix = $$props.prefix);
    		if ("restoreScrollState" in $$props) $$invalidate(5, restoreScrollState = $$props.restoreScrollState);
    		if ("component" in $$props) $$invalidate(0, component = $$props.component);
    		if ("componentParams" in $$props) $$invalidate(1, componentParams = $$props.componentParams);
    		if ("props" in $$props) $$invalidate(2, props = $$props.props);
    		if ("previousScrollState" in $$props) previousScrollState = $$props.previousScrollState;
    		if ("lastLoc" in $$props) lastLoc = $$props.lastLoc;
    		if ("componentObj" in $$props) componentObj = $$props.componentObj;
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*restoreScrollState*/ 32) {
    			// Update history.scrollRestoration depending on restoreScrollState
    			 history.scrollRestoration = restoreScrollState ? "manual" : "auto";
    		}
    	};

    	return [
    		component,
    		componentParams,
    		props,
    		routes,
    		prefix,
    		restoreScrollState,
    		routeEvent_handler,
    		routeEvent_handler_1
    	];
    }

    class Router extends SvelteComponentDev {
    	constructor(options) {
    		super(options);

    		init(this, options, instance$2, create_fragment$2, safe_not_equal, {
    			routes: 3,
    			prefix: 4,
    			restoreScrollState: 5
    		});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "Router",
    			options,
    			id: create_fragment$2.name
    		});
    	}

    	get routes() {
    		throw new Error_1("<Router>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set routes(value) {
    		throw new Error_1("<Router>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get prefix() {
    		throw new Error_1("<Router>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set prefix(value) {
    		throw new Error_1("<Router>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get restoreScrollState() {
    		throw new Error_1("<Router>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set restoreScrollState(value) {
    		throw new Error_1("<Router>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/views/DocFrame.svelte generated by Svelte v3.24.1 */

    const file$2 = "src/views/DocFrame.svelte";

    function create_fragment$3(ctx) {
    	let iframe;
    	let iframe_src_value;

    	const block = {
    		c: function create() {
    			iframe = element("iframe");
    			attr_dev(iframe, "title", /*title*/ ctx[1]);
    			if (iframe.src !== (iframe_src_value = /*source*/ ctx[0])) attr_dev(iframe, "src", iframe_src_value);
    			attr_dev(iframe, "class", "svelte-2gd2b0");
    			add_location(iframe, file$2, 6, 0, 110);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, iframe, anchor);
    		},
    		p: function update(ctx, [dirty]) {
    			if (dirty & /*title*/ 2) {
    				attr_dev(iframe, "title", /*title*/ ctx[1]);
    			}

    			if (dirty & /*source*/ 1 && iframe.src !== (iframe_src_value = /*source*/ ctx[0])) {
    				attr_dev(iframe, "src", iframe_src_value);
    			}
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(iframe);
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
    	let { source = null } = $$props;
    	let { title = null } = $$props;
    	const writable_props = ["source", "title"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<DocFrame> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("DocFrame", $$slots, []);

    	$$self.$$set = $$props => {
    		if ("source" in $$props) $$invalidate(0, source = $$props.source);
    		if ("title" in $$props) $$invalidate(1, title = $$props.title);
    	};

    	$$self.$capture_state = () => ({ source, title });

    	$$self.$inject_state = $$props => {
    		if ("source" in $$props) $$invalidate(0, source = $$props.source);
    		if ("title" in $$props) $$invalidate(1, title = $$props.title);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*title*/ 2) {
    			 document.title = title;
    		}
    	};

    	return [source, title];
    }

    class DocFrame extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$3, create_fragment$3, safe_not_equal, { source: 0, title: 1 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "DocFrame",
    			options,
    			id: create_fragment$3.name
    		});
    	}

    	get source() {
    		throw new Error("<DocFrame>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set source(value) {
    		throw new Error("<DocFrame>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get title() {
    		throw new Error("<DocFrame>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set title(value) {
    		throw new Error("<DocFrame>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    function toastSuccess(message) {
        toast.push(message, {
            theme: {
                '--toastBackground': '#48BB78',
                '--toastProgressBackground': '#2F855A',
            }
        });
    }


    function toastFail(message) {
        toast.push(message, {
            theme: {
                '--toastBackground': '#F56565',
                '--toastProgressBackground': '#C53030',
            }
        });
    }

    function toastClear() {
        toast.pop();
    }

    function toastOnCondition(condition, message) {
        if (condition) {
            message += ": Success";
            toastSuccess(message);
        } else {
            message += ": Failed";
            toastFail(message);
        }
    }

    class Entity {

        constructor(data) {
            this._data = data;
        }

        get key() {
            return this._data["key"];
        }

        set key(value) {
            this._data["key"] = value;
        }

        get label() {
            return this._data["label"];
        }

        set label(value) {
            this._data["label"] = value;
        }

        get name() {
            return this._data["name"];
        }

        set name(value) {
            this._data["name"] = value;
        }

        get attributes() {
            const attributes = {};

            for (const [key, value] of  Object.entries(this._data || {})) {
                if (!["key", "name", "label"].includes(key)) {
                    if (value === '' || value === null || value === undefined) continue;
                    if (value instanceof Array && value.length === 0) continue;
                    attributes[key] = value;
                }
            }

            return Object.entries(attributes).sort();
        }

        get body() {
            const body = {};

            for (const [key, value] of  Object.entries(this._data || {})) {
                if (value === '' || value === null || value === undefined) continue;
                if (value instanceof Array && value.length === 0) continue;
                body[key] = value;
            }

            return body;
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

    const findOneURL = baseURL + "/find_one";
    const getNodeURL = baseURL + "/nodes/";
    const getNeighborsURL = baseURL + "/nodes/neighbors";
    const getNodeCountURL = baseURL + "/nodes/count";
    const searchURL = baseURL + "/search";
    const getSchemaURL = baseURL + "/meta/schema";
    const parseURL = baseURL + "/parse";
    const saveNodeURL = baseURL + "/nodes";


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

        async getSchema() {
            return await fetch(getSchemaURL, {
                ...defaultParams,
                method: "GET",
            })
                .then(response => {
                    if (!response.ok) {
                        return Promise.reject(response);
                    }
                    return response.json()
                })
                .catch(async response => {
                    console.log(response);
                    return {labels: [], verbs: []}
                });
        }

        async findOne(key) {
            const words = key.split("|");
            const text = words[0];
            const label = words[1];

            const body = JSON.stringify({text: text, labels: [label]});

            const data = await fetch(findOneURL, {
                ...defaultParams,
                method: "POST",
                body: body,
            })
                .then(response => {
                    if (!response.ok) {
                        return Promise.reject(response);
                    }
                    return response.json()
                })
                .catch(async response => {
                    console.log(response);
                    return null;
                });

            return data ? new Entity(data) : null;
        }

        async getNode(key) {
            // double encoding required to send correctly.
            key = encodeURIComponent(encodeURIComponent(key));
            const data = await fetch(getNodeURL + key, {
                ...defaultParams,
                method: "GET",
            })
                .then(response => {
                    if (!response.ok) {
                        return Promise.reject(response);
                    }
                    return response.json()
                })
                .catch(async response => {
                    console.log(response);
                    return null;
                });

            return data ? new Entity(data) : null;
        }
        async getNeighbors(thisRequest) {
            thisRequest["direction"] = thisRequest["direction"] || null;
            thisRequest["offset"] = thisRequest["page"] * 10;
            thisRequest["limit"] = 10;
            console.log(thisRequest);

            const body = JSON.stringify(thisRequest);

            // noinspection DuplicatedCode
            return await fetch(getNeighborsURL, {
                ...defaultParams,
                method: "POST",
                body: body,
            })
                .then(response => {
                    if (!response.ok) {
                        return Promise.reject(response);
                    }
                    return response.json()
                })
                .catch(async response => {
                    console.log(await response.text());
                    return null;
                });
        }

        async getNeighbors_old(thisRequest) {
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
            const request = new SearchRequest(null, null, keys, traversal, thisRequest.page);
            const response = await this.doSearch(request);

            if (response) {
                let nodes = new Map(response.nodes.map(node => [node.key, node]));
                return response.trails.map(trail => new Neighbor(trail, nodes.get(trail.end)));
            } else {
                return false;
            }
        }

        async getEntities(thisRequest) {
            let traversal = new Traversal();
            const request = new SearchRequest(
                thisRequest.q, thisRequest.labels, [], traversal, thisRequest.page
            );
            const response = await this.doSearch(request);
            if (response && response.nodes) {
                return response.nodes.map(data => new Entity(data));
            } else {
                return [];
            }
        }
        async getTotalCount(thisRequest) {
            const body = JSON.stringify({
                term: thisRequest.q || null,
                labels: thisRequest.labels || [],
            });

            return await fetch(getNodeCountURL, {
                ...defaultParams,
                method: "POST",
                body: body,
            })
                .then(response => {
                    if (!response.ok) {
                        return Promise.reject(response);
                    }
                    return response.json()
                })
                .catch(async response => {
                    console.log(await response.text());
                    return null;
                });
        }

        async doSearch(request) {
            const body = JSON.stringify(request);

            return await fetch(searchURL, {
                ...defaultParams,
                method: "POST",
                body: body,
            })
                .then(response => {
                    if (!response.ok) {
                        return Promise.reject(response);
                    }
                    return response.json()
                })
                .catch(async response => {
                    console.log(response);
                    return {nodes: [], trails: []};
                });
        }

        async parseDoc(thisRequest) {
            const body = JSON.stringify(thisRequest);

            return await fetch(parseURL, {
                ...defaultParams,
                method: "POST",
                body: body,
            })
                .then(response => {
                    if (!response.ok) {
                        return Promise.reject(response);
                    }
                    return response.json()
                })
                .catch(async response => {
                    console.log(response);
                    return {
                        text: thisRequest.text,
                        spans: [],
                        tokens: []
                    }
                });
        }

        async saveEntity(entity) {
            const body = JSON.stringify(entity.body);

            return await fetch(saveNodeURL, {
                ...defaultParams,
                method: "POST",
                body: body,
            }).then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    return false;
                }
            }).catch(async response => {
                console.log(response);
                return false;
            });
        }
    }

    const manager = new RequestManager();

    let _instance = null;

    class Schema {

        constructor() {
            this.data = null;
        }

        get labels() {
            return (this.data && this.data.labels) || [];
        }

        get verbs() {
            return (this.data && this.data.verbs) || [];
        }

        async load(force) {
            if (force || this.data === null) {
                this.data = await manager.getSchema();
            }
        }

        getNode(label) {
            return this.data.nodes[label];
        }

        get labelOptions() {
            const options = {};
            this.labels.map(label => {options[label] = label;});
            return options;
        }
    }

    Schema.instance = () => {
        if (_instance === null) {
            _instance = new Schema();
        }
        return _instance;
    };

    /* src/common/ColumnFilter.svelte generated by Svelte v3.24.1 */
    const file$3 = "src/common/ColumnFilter.svelte";

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
    			attr_dev(i, "class", "blue filter icon svelte-1xmvxjb");
    			add_location(i, file$3, 40, 12, 1096);
    			attr_dev(a, "href", "javascript:void(0)");
    			attr_dev(a, "class", "clickable");
    			add_location(a, file$3, 39, 8, 1014);
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
    function create_if_block$2(ctx) {
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
    			attr_dev(i, "class", "red window close icon svelte-1xmvxjb");
    			add_location(i, file$3, 26, 12, 600);
    			attr_dev(a, "class", "clickable");
    			add_location(a, file$3, 25, 8, 542);
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
    		id: create_if_block$2.name,
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
    			add_location(input, file$3, 36, 12, 919);
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
    			add_location(option, file$3, 30, 16, 729);
    			if (/*value*/ ctx[0] === void 0) add_render_callback(() => /*select_change_handler*/ ctx[7].call(select));
    			add_location(select, file$3, 29, 12, 685);
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
    			add_location(option, file$3, 32, 16, 823);
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

    function create_fragment$4(ctx) {
    	let div;

    	function select_block_type(ctx, dirty) {
    		if (/*inFilterMode*/ ctx[3]) return create_if_block$2;
    		return create_else_block_1;
    	}

    	let current_block_type = select_block_type(ctx);
    	let if_block = current_block_type(ctx);

    	const block = {
    		c: function create() {
    			div = element("div");
    			if_block.c();
    			attr_dev(div, "id", "column");
    			attr_dev(div, "class", "svelte-1xmvxjb");
    			add_location(div, file$3, 23, 0, 493);
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
    		onMount,
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

    		init(this, options, instance$4, create_fragment$4, safe_not_equal, {
    			name: 6,
    			value: 0,
    			display: 1,
    			options: 2
    		});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "ColumnFilter",
    			options,
    			id: create_fragment$4.name
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

    /* src/common/Pagination.svelte generated by Svelte v3.24.1 */
    const file$4 = "src/common/Pagination.svelte";

    // (51:4) {#if page_max}
    function create_if_block$3(ctx) {
    	let t0;
    	let t1;
    	let t2;
    	let t3;
    	let if_block_anchor;
    	let if_block = /*total_count*/ ctx[0] !== null && create_if_block_1$1(ctx);

    	const block = {
    		c: function create() {
    			t0 = text(/*page_min*/ ctx[1]);
    			t1 = text(" - ");
    			t2 = text(/*page_max*/ ctx[2]);
    			t3 = space();
    			if (if_block) if_block.c();
    			if_block_anchor = empty();
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, t0, anchor);
    			insert_dev(target, t1, anchor);
    			insert_dev(target, t2, anchor);
    			insert_dev(target, t3, anchor);
    			if (if_block) if_block.m(target, anchor);
    			insert_dev(target, if_block_anchor, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*page_min*/ 2) set_data_dev(t0, /*page_min*/ ctx[1]);
    			if (dirty & /*page_max*/ 4) set_data_dev(t2, /*page_max*/ ctx[2]);

    			if (/*total_count*/ ctx[0] !== null) {
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
    			if (detaching) detach_dev(t0);
    			if (detaching) detach_dev(t1);
    			if (detaching) detach_dev(t2);
    			if (detaching) detach_dev(t3);
    			if (if_block) if_block.d(detaching);
    			if (detaching) detach_dev(if_block_anchor);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$3.name,
    		type: "if",
    		source: "(51:4) {#if page_max}",
    		ctx
    	});

    	return block;
    }

    // (53:8) {#if total_count !== null}
    function create_if_block_1$1(ctx) {
    	let t0;
    	let t1;

    	const block = {
    		c: function create() {
    			t0 = text("of ");
    			t1 = text(/*total_count*/ ctx[0]);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, t0, anchor);
    			insert_dev(target, t1, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*total_count*/ 1) set_data_dev(t1, /*total_count*/ ctx[0]);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(t0);
    			if (detaching) detach_dev(t1);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_1$1.name,
    		type: "if",
    		source: "(53:8) {#if total_count !== null}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$5(ctx) {
    	let div;
    	let button0;
    	let i0;
    	let t0;
    	let button1;
    	let i1;
    	let t1;
    	let t2;
    	let button2;
    	let i2;
    	let mounted;
    	let dispose;
    	let if_block = /*page_max*/ ctx[2] && create_if_block$3(ctx);

    	const block = {
    		c: function create() {
    			div = element("div");
    			button0 = element("button");
    			i0 = element("i");
    			t0 = space();
    			button1 = element("button");
    			i1 = element("i");
    			t1 = text("\n\n     \n\n    ");
    			if (if_block) if_block.c();
    			t2 = text("\n\n     \n\n    ");
    			button2 = element("button");
    			i2 = element("i");
    			attr_dev(i0, "class", "angle double left icon");
    			add_location(i0, file$4, 39, 8, 968);
    			attr_dev(button0, "class", "circular ui icon button");
    			toggle_class(button0, "disabled", !/*has_prev*/ ctx[3]);
    			add_location(button0, file$4, 36, 4, 847);
    			attr_dev(i1, "class", "angle left icon");
    			add_location(i1, file$4, 45, 8, 1150);
    			attr_dev(button1, "class", "circular ui icon button");
    			toggle_class(button1, "disabled", !/*has_prev*/ ctx[3]);
    			add_location(button1, file$4, 42, 4, 1026);
    			attr_dev(i2, "class", "angle right icon");
    			add_location(i2, file$4, 62, 8, 1485);
    			attr_dev(button2, "class", "circular ui icon button");
    			toggle_class(button2, "disabled", !/*has_next*/ ctx[4]);
    			add_location(button2, file$4, 59, 4, 1365);
    			attr_dev(div, "id", "pagination");
    			attr_dev(div, "class", "svelte-oqtjm1");
    			add_location(div, file$4, 35, 0, 821);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			append_dev(div, button0);
    			append_dev(button0, i0);
    			append_dev(div, t0);
    			append_dev(div, button1);
    			append_dev(button1, i1);
    			append_dev(div, t1);
    			if (if_block) if_block.m(div, null);
    			append_dev(div, t2);
    			append_dev(div, button2);
    			append_dev(button2, i2);

    			if (!mounted) {
    				dispose = [
    					listen_dev(button0, "click", /*firstPage*/ ctx[5], false, false, false),
    					listen_dev(button1, "click", /*previousPage*/ ctx[6], false, false, false),
    					listen_dev(button2, "click", /*nextPage*/ ctx[7], false, false, false)
    				];

    				mounted = true;
    			}
    		},
    		p: function update(ctx, [dirty]) {
    			if (dirty & /*has_prev*/ 8) {
    				toggle_class(button0, "disabled", !/*has_prev*/ ctx[3]);
    			}

    			if (dirty & /*has_prev*/ 8) {
    				toggle_class(button1, "disabled", !/*has_prev*/ ctx[3]);
    			}

    			if (/*page_max*/ ctx[2]) {
    				if (if_block) {
    					if_block.p(ctx, dirty);
    				} else {
    					if_block = create_if_block$3(ctx);
    					if_block.c();
    					if_block.m(div, t2);
    				}
    			} else if (if_block) {
    				if_block.d(1);
    				if_block = null;
    			}

    			if (dirty & /*has_next*/ 16) {
    				toggle_class(button2, "disabled", !/*has_next*/ ctx[4]);
    			}
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    			if (if_block) if_block.d();
    			mounted = false;
    			run_all(dispose);
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
    	const dispatch = createEventDispatcher();
    	let { page = 0 } = $$props;
    	let { page_size = 10 } = $$props;
    	let { page_count = 0 } = $$props;
    	let { total_count = null } = $$props;
    	let page_min = 0;
    	let page_max = 0;
    	let has_prev = false;
    	let has_next = false;

    	const update_nums = () => {
    		$$invalidate(1, page_min = page * page_size + 1);
    		$$invalidate(2, page_max = page * page_size + page_count);
    		$$invalidate(3, has_prev = page > 0);
    		$$invalidate(4, has_next = page_max < total_count);
    	};

    	function firstPage() {
    		dispatch("doPageChange", 0);
    	}

    	function previousPage() {
    		dispatch("doPageChange", page - 1);
    	}

    	function nextPage() {
    		dispatch("doPageChange", page + 1);
    	}

    	const writable_props = ["page", "page_size", "page_count", "total_count"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<Pagination> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("Pagination", $$slots, []);

    	$$self.$$set = $$props => {
    		if ("page" in $$props) $$invalidate(8, page = $$props.page);
    		if ("page_size" in $$props) $$invalidate(9, page_size = $$props.page_size);
    		if ("page_count" in $$props) $$invalidate(10, page_count = $$props.page_count);
    		if ("total_count" in $$props) $$invalidate(0, total_count = $$props.total_count);
    	};

    	$$self.$capture_state = () => ({
    		createEventDispatcher,
    		dispatch,
    		page,
    		page_size,
    		page_count,
    		total_count,
    		page_min,
    		page_max,
    		has_prev,
    		has_next,
    		update_nums,
    		firstPage,
    		previousPage,
    		nextPage
    	});

    	$$self.$inject_state = $$props => {
    		if ("page" in $$props) $$invalidate(8, page = $$props.page);
    		if ("page_size" in $$props) $$invalidate(9, page_size = $$props.page_size);
    		if ("page_count" in $$props) $$invalidate(10, page_count = $$props.page_count);
    		if ("total_count" in $$props) $$invalidate(0, total_count = $$props.total_count);
    		if ("page_min" in $$props) $$invalidate(1, page_min = $$props.page_min);
    		if ("page_max" in $$props) $$invalidate(2, page_max = $$props.page_max);
    		if ("has_prev" in $$props) $$invalidate(3, has_prev = $$props.has_prev);
    		if ("has_next" in $$props) $$invalidate(4, has_next = $$props.has_next);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*page, page_size, page_count*/ 1792) {
    			 update_nums();
    		}
    	};

    	return [
    		total_count,
    		page_min,
    		page_max,
    		has_prev,
    		has_next,
    		firstPage,
    		previousPage,
    		nextPage,
    		page,
    		page_size,
    		page_count
    	];
    }

    class Pagination extends SvelteComponentDev {
    	constructor(options) {
    		super(options);

    		init(this, options, instance$5, create_fragment$5, safe_not_equal, {
    			page: 8,
    			page_size: 9,
    			page_count: 10,
    			total_count: 0
    		});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "Pagination",
    			options,
    			id: create_fragment$5.name
    		});
    	}

    	get page() {
    		throw new Error("<Pagination>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set page(value) {
    		throw new Error("<Pagination>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get page_size() {
    		throw new Error("<Pagination>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set page_size(value) {
    		throw new Error("<Pagination>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get page_count() {
    		throw new Error("<Pagination>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set page_count(value) {
    		throw new Error("<Pagination>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get total_count() {
    		throw new Error("<Pagination>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set total_count(value) {
    		throw new Error("<Pagination>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/views/NodeDetail.svelte generated by Svelte v3.24.1 */

    const { Object: Object_1$2, console: console_1$1 } = globals;
    const file$5 = "src/views/NodeDetail.svelte";

    function get_each_context$2(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[16] = list[i];
    	return child_ctx;
    }

    function get_each_context_3(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[26] = list[i];
    	return child_ctx;
    }

    function get_each_context_2(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[23] = list[i];
    	return child_ctx;
    }

    function get_each_context_1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[19] = list[i][0];
    	child_ctx[20] = list[i][1];
    	return child_ctx;
    }

    // (87:0) {#if entity && schema}
    function create_if_block$4(ctx) {
    	let div7;
    	let div0;
    	let h20;
    	let t1;
    	let table0;
    	let tbody0;
    	let tr0;
    	let td0;
    	let t3;
    	let td1;
    	let t4_value = /*entity*/ ctx[0].name + "";
    	let t4;
    	let t5;
    	let tr1;
    	let td2;
    	let t7;
    	let td3;
    	let t8_value = /*entity*/ ctx[0].label + "";
    	let t8;
    	let t9;
    	let tr2;
    	let td4;
    	let t11;
    	let td5;
    	let t12_value = /*entity*/ ctx[0].key + "";
    	let t12;
    	let t13;
    	let t14;
    	let div6;
    	let div5;
    	let div4;
    	let div1;
    	let h21;
    	let t16;
    	let div2;
    	let t17;
    	let div3;
    	let t18;
    	let table1;
    	let thead;
    	let tr3;
    	let th0;
    	let columnfilter0;
    	let t19;
    	let th1;
    	let columnfilter1;
    	let t20;
    	let th2;
    	let t22;
    	let th3;
    	let columnfilter2;
    	let t23;
    	let tbody1;
    	let current;
    	let each_value_1 = /*entity*/ ctx[0].attributes;
    	validate_each_argument(each_value_1);
    	let each_blocks = [];

    	for (let i = 0; i < each_value_1.length; i += 1) {
    		each_blocks[i] = create_each_block_1(get_each_context_1(ctx, each_value_1, i));
    	}

    	let if_block0 = /*neighbors*/ ctx[1] && create_if_block_4(ctx);

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
    				options: /*schema*/ ctx[4].verbs
    			},
    			$$inline: true
    		});

    	columnfilter1.$on("update", /*onUpdate*/ ctx[6]);

    	columnfilter2 = new ColumnFilter({
    			props: {
    				name: "label",
    				display: "Label",
    				options: /*schema*/ ctx[4].labels
    			},
    			$$inline: true
    		});

    	columnfilter2.$on("update", /*onUpdate*/ ctx[6]);

    	function select_block_type_1(ctx, dirty) {
    		if (!/*neighbors*/ ctx[1]) return create_if_block_1$2;
    		return create_else_block_1$1;
    	}

    	let current_block_type = select_block_type_1(ctx);
    	let if_block1 = current_block_type(ctx);

    	const block = {
    		c: function create() {
    			div7 = element("div");
    			div0 = element("div");
    			h20 = element("h2");
    			h20.textContent = "Node Details";
    			t1 = space();
    			table0 = element("table");
    			tbody0 = element("tbody");
    			tr0 = element("tr");
    			td0 = element("td");
    			td0.textContent = "name:";
    			t3 = space();
    			td1 = element("td");
    			t4 = text(t4_value);
    			t5 = space();
    			tr1 = element("tr");
    			td2 = element("td");
    			td2.textContent = "label:";
    			t7 = space();
    			td3 = element("td");
    			t8 = text(t8_value);
    			t9 = space();
    			tr2 = element("tr");
    			td4 = element("td");
    			td4.textContent = "key:";
    			t11 = space();
    			td5 = element("td");
    			t12 = text(t12_value);
    			t13 = space();

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			t14 = space();
    			div6 = element("div");
    			div5 = element("div");
    			div4 = element("div");
    			div1 = element("div");
    			h21 = element("h2");
    			h21.textContent = "Relationships";
    			t16 = space();
    			div2 = element("div");
    			t17 = space();
    			div3 = element("div");
    			if (if_block0) if_block0.c();
    			t18 = space();
    			table1 = element("table");
    			thead = element("thead");
    			tr3 = element("tr");
    			th0 = element("th");
    			create_component(columnfilter0.$$.fragment);
    			t19 = space();
    			th1 = element("th");
    			create_component(columnfilter1.$$.fragment);
    			t20 = space();
    			th2 = element("th");
    			th2.textContent = "Name";
    			t22 = space();
    			th3 = element("th");
    			create_component(columnfilter2.$$.fragment);
    			t23 = space();
    			tbody1 = element("tbody");
    			if_block1.c();
    			attr_dev(h20, "class", "svelte-1q6tlf6");
    			add_location(h20, file$5, 89, 12, 2397);
    			attr_dev(td0, "class", "two wide column");
    			add_location(td0, file$5, 93, 20, 2544);
    			attr_dev(td1, "class", "five wide column");
    			add_location(td1, file$5, 94, 20, 2603);
    			add_location(tr0, file$5, 92, 16, 2519);
    			add_location(td2, file$5, 97, 20, 2714);
    			add_location(td3, file$5, 98, 20, 2750);
    			add_location(tr1, file$5, 96, 16, 2689);
    			add_location(td4, file$5, 101, 20, 2837);
    			add_location(td5, file$5, 102, 20, 2871);
    			add_location(tr2, file$5, 100, 16, 2812);
    			add_location(tbody0, file$5, 91, 16, 2495);
    			attr_dev(table0, "class", "ui definition table top aligned");
    			add_location(table0, file$5, 90, 12, 2431);
    			attr_dev(div0, "class", "six wide column");
    			add_location(div0, file$5, 88, 8, 2355);
    			attr_dev(h21, "class", "svelte-1q6tlf6");
    			add_location(h21, file$5, 143, 24, 4684);
    			attr_dev(div1, "class", "column");
    			add_location(div1, file$5, 142, 20, 4639);
    			attr_dev(div2, "class", "ten wide column");
    			add_location(div2, file$5, 145, 20, 4754);
    			attr_dev(div3, "class", "column");
    			add_location(div3, file$5, 146, 20, 4810);
    			attr_dev(div4, "class", "row");
    			add_location(div4, file$5, 141, 16, 4601);
    			attr_dev(div5, "class", "ui grid");
    			add_location(div5, file$5, 140, 12, 4563);
    			attr_dev(th0, "class", "two wide");
    			attr_dev(th0, "nowrap", "nowrap");
    			add_location(th0, file$5, 161, 20, 5412);
    			attr_dev(th1, "class", "two wide");
    			attr_dev(th1, "nowrap", "nowrap");
    			add_location(th1, file$5, 167, 20, 5729);
    			attr_dev(th2, "class", "three wide");
    			attr_dev(th2, "nowrap", "nowrap");
    			add_location(th2, file$5, 172, 20, 6000);
    			attr_dev(th3, "class", "two wide");
    			add_location(th3, file$5, 176, 20, 6230);
    			add_location(tr3, file$5, 160, 16, 5387);
    			attr_dev(thead, "class", "full-width");
    			add_location(thead, file$5, 159, 16, 5344);
    			add_location(tbody1, file$5, 183, 12, 6527);
    			attr_dev(table1, "class", "ui striped selectable celled table top aligned");
    			add_location(table1, file$5, 158, 12, 5265);
    			attr_dev(div6, "class", "ten wide column");
    			add_location(div6, file$5, 139, 8, 4521);
    			attr_dev(div7, "class", "ui stackable two column grid");
    			add_location(div7, file$5, 87, 4, 2304);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div7, anchor);
    			append_dev(div7, div0);
    			append_dev(div0, h20);
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

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(tbody0, null);
    			}

    			append_dev(div7, t14);
    			append_dev(div7, div6);
    			append_dev(div6, div5);
    			append_dev(div5, div4);
    			append_dev(div4, div1);
    			append_dev(div1, h21);
    			append_dev(div4, t16);
    			append_dev(div4, div2);
    			append_dev(div4, t17);
    			append_dev(div4, div3);
    			if (if_block0) if_block0.m(div3, null);
    			append_dev(div6, t18);
    			append_dev(div6, table1);
    			append_dev(table1, thead);
    			append_dev(thead, tr3);
    			append_dev(tr3, th0);
    			mount_component(columnfilter0, th0, null);
    			append_dev(tr3, t19);
    			append_dev(tr3, th1);
    			mount_component(columnfilter1, th1, null);
    			append_dev(tr3, t20);
    			append_dev(tr3, th2);
    			append_dev(tr3, t22);
    			append_dev(tr3, th3);
    			mount_component(columnfilter2, th3, null);
    			append_dev(table1, t23);
    			append_dev(table1, tbody1);
    			if_block1.m(tbody1, null);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			if ((!current || dirty & /*entity*/ 1) && t4_value !== (t4_value = /*entity*/ ctx[0].name + "")) set_data_dev(t4, t4_value);
    			if ((!current || dirty & /*entity*/ 1) && t8_value !== (t8_value = /*entity*/ ctx[0].label + "")) set_data_dev(t8, t8_value);
    			if ((!current || dirty & /*entity*/ 1) && t12_value !== (t12_value = /*entity*/ ctx[0].key + "")) set_data_dev(t12, t12_value);

    			if (dirty & /*entity, Array, Object*/ 1) {
    				each_value_1 = /*entity*/ ctx[0].attributes;
    				validate_each_argument(each_value_1);
    				let i;

    				for (i = 0; i < each_value_1.length; i += 1) {
    					const child_ctx = get_each_context_1(ctx, each_value_1, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block_1(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(tbody0, null);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value_1.length;
    			}

    			if (/*neighbors*/ ctx[1]) {
    				if (if_block0) {
    					if_block0.p(ctx, dirty);

    					if (dirty & /*neighbors*/ 2) {
    						transition_in(if_block0, 1);
    					}
    				} else {
    					if_block0 = create_if_block_4(ctx);
    					if_block0.c();
    					transition_in(if_block0, 1);
    					if_block0.m(div3, null);
    				}
    			} else if (if_block0) {
    				group_outros();

    				transition_out(if_block0, 1, 1, () => {
    					if_block0 = null;
    				});

    				check_outros();
    			}

    			if (current_block_type === (current_block_type = select_block_type_1(ctx)) && if_block1) {
    				if_block1.p(ctx, dirty);
    			} else {
    				if_block1.d(1);
    				if_block1 = current_block_type(ctx);

    				if (if_block1) {
    					if_block1.c();
    					if_block1.m(tbody1, null);
    				}
    			}
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(if_block0);
    			transition_in(columnfilter0.$$.fragment, local);
    			transition_in(columnfilter1.$$.fragment, local);
    			transition_in(columnfilter2.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(if_block0);
    			transition_out(columnfilter0.$$.fragment, local);
    			transition_out(columnfilter1.$$.fragment, local);
    			transition_out(columnfilter2.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div7);
    			destroy_each(each_blocks, detaching);
    			if (if_block0) if_block0.d();
    			destroy_component(columnfilter0);
    			destroy_component(columnfilter1);
    			destroy_component(columnfilter2);
    			if_block1.d();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$4.name,
    		type: "if",
    		source: "(87:0) {#if entity && schema}",
    		ctx
    	});

    	return block;
    }

    // (124:28) {:else}
    function create_else_block_2(ctx) {
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
    		id: create_else_block_2.name,
    		type: "else",
    		source: "(124:28) {:else}",
    		ctx
    	});

    	return block;
    }

    // (122:100) 
    function create_if_block_7(ctx) {
    	let a;
    	let t_value = /*value*/ ctx[20] + "";
    	let t;
    	let a_href_value;

    	const block = {
    		c: function create() {
    			a = element("a");
    			t = text(t_value);
    			attr_dev(a, "target", "_blank");
    			attr_dev(a, "href", a_href_value = /*value*/ ctx[20]);
    			add_location(a, file$5, 122, 32, 3919);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, a, anchor);
    			append_dev(a, t);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*entity*/ 1 && t_value !== (t_value = /*value*/ ctx[20] + "")) set_data_dev(t, t_value);

    			if (dirty & /*entity*/ 1 && a_href_value !== (a_href_value = /*value*/ ctx[20])) {
    				attr_dev(a, "href", a_href_value);
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(a);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_7.name,
    		type: "if",
    		source: "(122:100) ",
    		ctx
    	});

    	return block;
    }

    // (113:62) 
    function create_if_block_6(ctx) {
    	let table;
    	let each_value_3 = Object.entries(/*value*/ ctx[20]);
    	validate_each_argument(each_value_3);
    	let each_blocks = [];

    	for (let i = 0; i < each_value_3.length; i += 1) {
    		each_blocks[i] = create_each_block_3(get_each_context_3(ctx, each_value_3, i));
    	}

    	const block = {
    		c: function create() {
    			table = element("table");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			attr_dev(table, "class", "ui compact celled table top aligned");
    			add_location(table, file$5, 113, 32, 3363);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, table, anchor);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(table, null);
    			}
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*Object, entity*/ 1) {
    				each_value_3 = Object.entries(/*value*/ ctx[20]);
    				validate_each_argument(each_value_3);
    				let i;

    				for (i = 0; i < each_value_3.length; i += 1) {
    					const child_ctx = get_each_context_3(ctx, each_value_3, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block_3(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(table, null);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value_3.length;
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(table);
    			destroy_each(each_blocks, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_6.name,
    		type: "if",
    		source: "(113:62) ",
    		ctx
    	});

    	return block;
    }

    // (109:28) {#if value instanceof Array}
    function create_if_block_5(ctx) {
    	let each_1_anchor;
    	let each_value_2 = /*value*/ ctx[20];
    	validate_each_argument(each_value_2);
    	let each_blocks = [];

    	for (let i = 0; i < each_value_2.length; i += 1) {
    		each_blocks[i] = create_each_block_2(get_each_context_2(ctx, each_value_2, i));
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
    			if (dirty & /*entity*/ 1) {
    				each_value_2 = /*value*/ ctx[20];
    				validate_each_argument(each_value_2);
    				let i;

    				for (i = 0; i < each_value_2.length; i += 1) {
    					const child_ctx = get_each_context_2(ctx, each_value_2, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block_2(child_ctx);
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
    		id: create_if_block_5.name,
    		type: "if",
    		source: "(109:28) {#if value instanceof Array}",
    		ctx
    	});

    	return block;
    }

    // (115:36) {#each Object.entries(value) as kv}
    function create_each_block_3(ctx) {
    	let tr;
    	let td0;
    	let t0_value = /*kv*/ ctx[26][0] + "";
    	let t0;
    	let t1;
    	let t2;
    	let td1;
    	let t3_value = /*kv*/ ctx[26][1] + "";
    	let t3;
    	let t4;

    	const block = {
    		c: function create() {
    			tr = element("tr");
    			td0 = element("td");
    			t0 = text(t0_value);
    			t1 = text(":");
    			t2 = space();
    			td1 = element("td");
    			t3 = text(t3_value);
    			t4 = space();
    			add_location(td0, file$5, 116, 44, 3576);
    			add_location(td1, file$5, 117, 44, 3638);
    			add_location(tr, file$5, 115, 40, 3527);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, tr, anchor);
    			append_dev(tr, td0);
    			append_dev(td0, t0);
    			append_dev(td0, t1);
    			append_dev(tr, t2);
    			append_dev(tr, td1);
    			append_dev(td1, t3);
    			append_dev(tr, t4);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*entity*/ 1 && t0_value !== (t0_value = /*kv*/ ctx[26][0] + "")) set_data_dev(t0, t0_value);
    			if (dirty & /*entity*/ 1 && t3_value !== (t3_value = /*kv*/ ctx[26][1] + "")) set_data_dev(t3, t3_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(tr);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block_3.name,
    		type: "each",
    		source: "(115:36) {#each Object.entries(value) as kv}",
    		ctx
    	});

    	return block;
    }

    // (110:32) {#each value as item}
    function create_each_block_2(ctx) {
    	let t_value = /*item*/ ctx[23] + "";
    	let t;
    	let br;

    	const block = {
    		c: function create() {
    			t = text(t_value);
    			br = element("br");
    			add_location(br, file$5, 110, 42, 3222);
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
    		id: create_each_block_2.name,
    		type: "each",
    		source: "(110:32) {#each value as item}",
    		ctx
    	});

    	return block;
    }

    // (105:16) {#each entity.attributes as [name, value]}
    function create_each_block_1(ctx) {
    	let tr;
    	let td0;
    	let t0_value = /*name*/ ctx[19] + "";
    	let t0;
    	let t1;
    	let t2;
    	let td1;
    	let show_if;
    	let t3;

    	function select_block_type(ctx, dirty) {
    		if (/*value*/ ctx[20] instanceof Array) return create_if_block_5;
    		if (/*value*/ ctx[20] instanceof Object) return create_if_block_6;
    		if (show_if == null || dirty & /*entity*/ 1) show_if = !!(/*value*/ ctx[20].startsWith("http://") || /*value*/ ctx[20].startsWith("https://"));
    		if (show_if) return create_if_block_7;
    		return create_else_block_2;
    	}

    	let current_block_type = select_block_type(ctx, -1);
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
    			add_location(td0, file$5, 106, 24, 3023);
    			add_location(td1, file$5, 107, 24, 3064);
    			add_location(tr, file$5, 105, 20, 2994);
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
    			if (dirty & /*entity*/ 1 && t0_value !== (t0_value = /*name*/ ctx[19] + "")) set_data_dev(t0, t0_value);

    			if (current_block_type === (current_block_type = select_block_type(ctx, dirty)) && if_block) {
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
    		source: "(105:16) {#each entity.attributes as [name, value]}",
    		ctx
    	});

    	return block;
    }

    // (148:24) {#if neighbors}
    function create_if_block_4(ctx) {
    	let pagination;
    	let current;

    	pagination = new Pagination({
    			props: {
    				page: /*nextRequest*/ ctx[3].page,
    				page_count: /*neighbors*/ ctx[1].length,
    				total_count: /*total_count*/ ctx[2]
    			},
    			$$inline: true
    		});

    	pagination.$on("doPageChange", /*doPageChange*/ ctx[7]);

    	const block = {
    		c: function create() {
    			create_component(pagination.$$.fragment);
    		},
    		m: function mount(target, anchor) {
    			mount_component(pagination, target, anchor);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			const pagination_changes = {};
    			if (dirty & /*nextRequest*/ 8) pagination_changes.page = /*nextRequest*/ ctx[3].page;
    			if (dirty & /*neighbors*/ 2) pagination_changes.page_count = /*neighbors*/ ctx[1].length;
    			if (dirty & /*total_count*/ 4) pagination_changes.total_count = /*total_count*/ ctx[2];
    			pagination.$set(pagination_changes);
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(pagination.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(pagination.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			destroy_component(pagination, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_4.name,
    		type: "if",
    		source: "(148:24) {#if neighbors}",
    		ctx
    	});

    	return block;
    }

    // (197:16) {:else}
    function create_else_block_1$1(ctx) {
    	let each_1_anchor;
    	let each_value = /*neighbors*/ ctx[1];
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block$2(get_each_context$2(ctx, each_value, i));
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
    			if (dirty & /*openRow, neighbors*/ 258) {
    				each_value = /*neighbors*/ ctx[1];
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context$2(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block$2(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(each_1_anchor.parentNode, each_1_anchor);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value.length;
    			}
    		},
    		d: function destroy(detaching) {
    			destroy_each(each_blocks, detaching);
    			if (detaching) detach_dev(each_1_anchor);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block_1$1.name,
    		type: "else",
    		source: "(197:16) {:else}",
    		ctx
    	});

    	return block;
    }

    // (185:16) {#if !neighbors}
    function create_if_block_1$2(ctx) {
    	let tr;
    	let td;

    	function select_block_type_2(ctx, dirty) {
    		if (/*neighbors*/ ctx[1] === null) return create_if_block_2;
    		if (/*neighbors*/ ctx[1] === false) return create_if_block_3;
    		return create_else_block$2;
    	}

    	let current_block_type = select_block_type_2(ctx);
    	let if_block = current_block_type(ctx);

    	const block = {
    		c: function create() {
    			tr = element("tr");
    			td = element("td");
    			if_block.c();
    			attr_dev(td, "class", "no-rels svelte-1q6tlf6");
    			attr_dev(td, "colspan", "4");
    			add_location(td, file$5, 186, 20, 6609);
    			add_location(tr, file$5, 185, 16, 6584);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, tr, anchor);
    			append_dev(tr, td);
    			if_block.m(td, null);
    		},
    		p: function update(ctx, dirty) {
    			if (current_block_type !== (current_block_type = select_block_type_2(ctx))) {
    				if_block.d(1);
    				if_block = current_block_type(ctx);

    				if (if_block) {
    					if_block.c();
    					if_block.m(td, null);
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
    		id: create_if_block_1$2.name,
    		type: "if",
    		source: "(185:16) {#if !neighbors}",
    		ctx
    	});

    	return block;
    }

    // (198:20) {#each neighbors as neighbor}
    function create_each_block$2(ctx) {
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
    	let t4_value = /*neighbor*/ ctx[16].node.name + "";
    	let t4;
    	let t5;
    	let td3;
    	let t6_value = /*neighbor*/ ctx[16].node.label + "";
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
    			add_location(td0, file$5, 199, 24, 7145);
    			add_location(td1, file$5, 200, 24, 7199);
    			add_location(td2, file$5, 201, 24, 7248);
    			add_location(td3, file$5, 202, 24, 7302);
    			add_location(tr, file$5, 198, 20, 7083);
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
    						if (is_function(/*openRow*/ ctx[8](/*neighbor*/ ctx[16].key))) /*openRow*/ ctx[8](/*neighbor*/ ctx[16].key).apply(this, arguments);
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
    			if (dirty & /*neighbors*/ 2 && t4_value !== (t4_value = /*neighbor*/ ctx[16].node.name + "")) set_data_dev(t4, t4_value);
    			if (dirty & /*neighbors*/ 2 && t6_value !== (t6_value = /*neighbor*/ ctx[16].node.label + "")) set_data_dev(t6, t6_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(tr);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block$2.name,
    		type: "each",
    		source: "(198:20) {#each neighbors as neighbor}",
    		ctx
    	});

    	return block;
    }

    // (192:24) {:else}
    function create_else_block$2(ctx) {
    	let t;

    	const block = {
    		c: function create() {
    			t = text("No relationships found.");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, t, anchor);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(t);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block$2.name,
    		type: "else",
    		source: "(192:24) {:else}",
    		ctx
    	});

    	return block;
    }

    // (190:54) 
    function create_if_block_3(ctx) {
    	let t;

    	const block = {
    		c: function create() {
    			t = text("Load failed.");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, t, anchor);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(t);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_3.name,
    		type: "if",
    		source: "(190:54) ",
    		ctx
    	});

    	return block;
    }

    // (188:24) {#if neighbors === null}
    function create_if_block_2(ctx) {
    	let t;

    	const block = {
    		c: function create() {
    			t = text("Loading....");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, t, anchor);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(t);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_2.name,
    		type: "if",
    		source: "(188:24) {#if neighbors === null}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$6(ctx) {
    	let if_block_anchor;
    	let current;
    	let if_block = /*entity*/ ctx[0] && /*schema*/ ctx[4] && create_if_block$4(ctx);

    	const block = {
    		c: function create() {
    			if (if_block) if_block.c();
    			if_block_anchor = empty();
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			if (if_block) if_block.m(target, anchor);
    			insert_dev(target, if_block_anchor, anchor);
    			current = true;
    		},
    		p: function update(ctx, [dirty]) {
    			if (/*entity*/ ctx[0] && /*schema*/ ctx[4]) {
    				if (if_block) {
    					if_block.p(ctx, dirty);

    					if (dirty & /*entity*/ 1) {
    						transition_in(if_block, 1);
    					}
    				} else {
    					if_block = create_if_block$4(ctx);
    					if_block.c();
    					transition_in(if_block, 1);
    					if_block.m(if_block_anchor.parentNode, if_block_anchor);
    				}
    			} else if (if_block) {
    				group_outros();

    				transition_out(if_block, 1, 1, () => {
    					if_block = null;
    				});

    				check_outros();
    			}
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(if_block);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(if_block);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (if_block) if_block.d(detaching);
    			if (detaching) detach_dev(if_block_anchor);
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
    	let { params = {} } = $$props;
    	let schema = Schema.instance();
    	let entity = null;
    	let neighbors = [];
    	let total_count = null;
    	let isDynamic = false;
    	let labelOptions = [];
    	let verbOptions = [];
    	const directions = ["incoming", "outgoing"];

    	const nextRequest = {
    		node_key: "",
    		verb: "",
    		direction: null,
    		name: "",
    		label: "",
    		page: 0
    	};

    	const loadEntity = async () => {
    		$$invalidate(0, entity = await manager.getNode(params.key));

    		if (!entity) {
    			$$invalidate(0, entity = await manager.findOne(params.key));
    			isDynamic = true;
    		}

    		if (entity) {
    			$$invalidate(3, nextRequest["node_key"] = entity.key, nextRequest);
    			await loadNeighbors();
    			document.title = `Detail: ${entity.name} [${entity.label}]`;
    		} else {
    			toastFail(`Failed to load: ${params.key}`);
    			await push("/");
    		}
    	};

    	const loadNeighbors = async () => {
    		$$invalidate(1, neighbors = null);

    		if (nextRequest.node_key) {
    			const response = await manager.getNeighbors(nextRequest);

    			if (response !== null) {
    				$$invalidate(1, neighbors = response.neighbors);
    				$$invalidate(2, total_count = response.total);
    			} else {
    				$$invalidate(1, neighbors = []);
    				$$invalidate(2, total_count = null);
    			}

    			console.log(neighbors);
    		}
    	};

    	const onUpdate = async event => {
    		$$invalidate(3, nextRequest[event.detail.name] = event.detail.value, nextRequest);
    		$$invalidate(3, nextRequest["page"] = 0, nextRequest);
    		await loadNeighbors();
    	};

    	async function doPageChange(event) {
    		$$invalidate(3, nextRequest["page"] = event.detail, nextRequest);
    		await loadNeighbors();
    	}

    	const openRow = key => {
    		const encodedKey = encodeURIComponent(key);
    		push("/detail/" + encodedKey);
    		$$invalidate(3, nextRequest["page"] = 0, nextRequest);
    	};

    	const openEdit = () => {
    		push("/edit/" + entity.key);
    	};

    	const writable_props = ["params"];

    	Object_1$2.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console_1$1.warn(`<NodeDetail> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("NodeDetail", $$slots, []);

    	$$self.$$set = $$props => {
    		if ("params" in $$props) $$invalidate(9, params = $$props.params);
    	};

    	$$self.$capture_state = () => ({
    		push,
    		pop,
    		toastFail,
    		manager,
    		Schema,
    		ColumnFilter,
    		Pagination,
    		params,
    		schema,
    		entity,
    		neighbors,
    		total_count,
    		isDynamic,
    		labelOptions,
    		verbOptions,
    		directions,
    		nextRequest,
    		loadEntity,
    		loadNeighbors,
    		onUpdate,
    		doPageChange,
    		openRow,
    		openEdit
    	});

    	$$self.$inject_state = $$props => {
    		if ("params" in $$props) $$invalidate(9, params = $$props.params);
    		if ("schema" in $$props) $$invalidate(4, schema = $$props.schema);
    		if ("entity" in $$props) $$invalidate(0, entity = $$props.entity);
    		if ("neighbors" in $$props) $$invalidate(1, neighbors = $$props.neighbors);
    		if ("total_count" in $$props) $$invalidate(2, total_count = $$props.total_count);
    		if ("isDynamic" in $$props) isDynamic = $$props.isDynamic;
    		if ("labelOptions" in $$props) labelOptions = $$props.labelOptions;
    		if ("verbOptions" in $$props) verbOptions = $$props.verbOptions;
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*params*/ 512) {
    			 loadEntity(params.key);
    		}
    	};

    	return [
    		entity,
    		neighbors,
    		total_count,
    		nextRequest,
    		schema,
    		directions,
    		onUpdate,
    		doPageChange,
    		openRow,
    		params
    	];
    }

    class NodeDetail extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$6, create_fragment$6, safe_not_equal, { params: 9 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "NodeDetail",
    			options,
    			id: create_fragment$6.name
    		});
    	}

    	get params() {
    		throw new Error("<NodeDetail>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set params(value) {
    		throw new Error("<NodeDetail>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    class Edit {

        constructor(entity, schema) {
            this.entity = entity;
            this.schema = schema;
            this.definition = null;
            this.properties = null;
            this.loadDefinition();

        }

        get title() {
            const defTitle = (this.definition && this.definition.title) || "New";
            if (this.isNew) {
                return `Create ${defTitle}`;
            } else {
                return `Edit ${defTitle}: ${this.name}`;
            }
        }

        isRequired(name) {
            return (this.definition.required || []).includes(name);
        }

        get isNew() {
            const value = this.key;
            return (value === '' || value === null || value === undefined);
        }

        get name() {
            return this.entity && this.entity.name;
        }

        set name(value) {
            this.data["name"] = value;
        }

        get label() {
            return this.entity && this.entity.label;
        }

        set label(value) {
            this.data["label"] = value;
            this.loadDefinition();
        }

        get key() {
            return this.entity && this.entity.key;
        }

        get data() {
            return this.entity && this.entity._data;
        }

        get attributes() {
            const attributes = [];

            for (const [name, prop] of this.properties) {
                if (!["key", "name", "label"].includes(name)) {
                    const type = prop["type"];
                    const title = prop["title"];
                    const required = this.isRequired(name);
                    const value = this.data[name];
                    const attr = {name, type, title, required, value};
                    attributes.push(attr);
                }
            }

            return attributes;
        }

        loadDefinition() {
            this.definition = (this.label ? this.schema.getNode(this.label) : null) || this.schema.getNode("ENTITY");
            this.properties = ((this.definition && Object.entries(this.definition["properties"])) || []).sort();
        }

    }

    /* src/common/FormTemplate.svelte generated by Svelte v3.24.1 */
    const file$6 = "src/common/FormTemplate.svelte";
    const get_fields_slot_changes = dirty => ({});
    const get_fields_slot_context = ctx => ({});
    const get_heading_slot_changes = dirty => ({});
    const get_heading_slot_context = ctx => ({});

    // (43:20) {:else}
    function create_else_block$3(ctx) {
    	let button;

    	const block = {
    		c: function create() {
    			button = element("button");
    			button.textContent = "Submit";
    			attr_dev(button, "class", "ui large primary button");
    			attr_dev(button, "type", "submit");
    			add_location(button, file$6, 43, 24, 1117);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, button, anchor);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(button);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block$3.name,
    		type: "else",
    		source: "(43:20) {:else}",
    		ctx
    	});

    	return block;
    }

    // (39:20) {#if waiting}
    function create_if_block_2$1(ctx) {
    	let button;

    	const block = {
    		c: function create() {
    			button = element("button");
    			button.textContent = "Loading";
    			attr_dev(button, "class", "ui large primary disabled loading button");
    			add_location(button, file$6, 39, 24, 937);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, button, anchor);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(button);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_2$1.name,
    		type: "if",
    		source: "(39:20) {#if waiting}",
    		ctx
    	});

    	return block;
    }

    // (55:8) {#if !dirty && error}
    function create_if_block_1$3(ctx) {
    	let div;
    	let t;

    	const block = {
    		c: function create() {
    			div = element("div");
    			t = text(/*error*/ ctx[1]);
    			attr_dev(div, "class", "ui visible error message");
    			add_location(div, file$6, 55, 12, 1543);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			append_dev(div, t);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*error*/ 2) set_data_dev(t, /*error*/ ctx[1]);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_1$3.name,
    		type: "if",
    		source: "(55:8) {#if !dirty && error}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$7(ctx) {
    	let div3;
    	let div2;
    	let div1;
    	let h2;
    	let t0;
    	let form;
    	let t1;
    	let div0;
    	let t2;
    	let span;
    	let a;
    	let t4;
    	let t5;
    	let current;
    	let mounted;
    	let dispose;
    	const heading_slot_template = /*$$slots*/ ctx[7].heading;
    	const heading_slot = create_slot(heading_slot_template, ctx, /*$$scope*/ ctx[6], get_heading_slot_context);
    	const fields_slot_template = /*$$slots*/ ctx[7].fields;
    	const fields_slot = create_slot(fields_slot_template, ctx, /*$$scope*/ ctx[6], get_fields_slot_context);

    	function select_block_type(ctx, dirty) {
    		if (/*waiting*/ ctx[0]) return create_if_block_2$1;
    		return create_else_block$3;
    	}

    	let current_block_type = select_block_type(ctx);
    	let if_block0 = current_block_type(ctx);
    	let if_block1 = !/*dirty*/ ctx[2] && /*error*/ ctx[1] && create_if_block_1$3(ctx);
    	let if_block2 = false ;

    	const block = {
    		c: function create() {
    			div3 = element("div");
    			div2 = element("div");
    			div1 = element("div");
    			h2 = element("h2");
    			if (heading_slot) heading_slot.c();
    			t0 = space();
    			form = element("form");
    			if (fields_slot) fields_slot.c();
    			t1 = space();
    			div0 = element("div");
    			if_block0.c();
    			t2 = space();
    			span = element("span");
    			a = element("a");
    			a.textContent = "Cancel";
    			t4 = space();
    			if (if_block1) if_block1.c();
    			t5 = space();
    			attr_dev(h2, "class", "svelte-ofyadh");
    			add_location(h2, file$6, 28, 12, 615);
    			attr_dev(a, "href", "javascript:void(0)");
    			attr_dev(a, "class", "svelte-ofyadh");
    			add_location(a, file$6, 48, 24, 1330);
    			attr_dev(span, "id", "cancel");
    			attr_dev(span, "class", "svelte-ofyadh");
    			add_location(span, file$6, 47, 20, 1287);
    			attr_dev(div0, "id", "buttons");
    			attr_dev(div0, "class", "svelte-ofyadh");
    			add_location(div0, file$6, 37, 16, 860);
    			attr_dev(form, "class", "ui large form");
    			attr_dev(form, "id", "formId");
    			add_location(form, file$6, 32, 12, 690);
    			attr_dev(div1, "class", "ui top attached stacked segment");
    			add_location(div1, file$6, 27, 8, 557);
    			attr_dev(div2, "class", "column svelte-ofyadh");
    			add_location(div2, file$6, 26, 4, 528);
    			attr_dev(div3, "id", "formContainer");
    			attr_dev(div3, "class", "ui aligned center aligned grid svelte-ofyadh");
    			add_location(div3, file$6, 25, 0, 460);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div3, anchor);
    			append_dev(div3, div2);
    			append_dev(div2, div1);
    			append_dev(div1, h2);

    			if (heading_slot) {
    				heading_slot.m(h2, null);
    			}

    			append_dev(div1, t0);
    			append_dev(div1, form);

    			if (fields_slot) {
    				fields_slot.m(form, null);
    			}

    			append_dev(form, t1);
    			append_dev(form, div0);
    			if_block0.m(div0, null);
    			append_dev(div0, t2);
    			append_dev(div0, span);
    			append_dev(span, a);
    			append_dev(div2, t4);
    			if (if_block1) if_block1.m(div2, null);
    			append_dev(div3, t5);
    			current = true;

    			if (!mounted) {
    				dispose = [
    					listen_dev(a, "click", /*cancel*/ ctx[4], false, false, false),
    					listen_dev(form, "submit", prevent_default(/*submit*/ ctx[3]), false, true, false),
    					listen_dev(form, "change", /*setDirty*/ ctx[5], false, false, false)
    				];

    				mounted = true;
    			}
    		},
    		p: function update(ctx, [dirty]) {
    			if (heading_slot) {
    				if (heading_slot.p && dirty & /*$$scope*/ 64) {
    					update_slot(heading_slot, heading_slot_template, ctx, /*$$scope*/ ctx[6], dirty, get_heading_slot_changes, get_heading_slot_context);
    				}
    			}

    			if (fields_slot) {
    				if (fields_slot.p && dirty & /*$$scope*/ 64) {
    					update_slot(fields_slot, fields_slot_template, ctx, /*$$scope*/ ctx[6], dirty, get_fields_slot_changes, get_fields_slot_context);
    				}
    			}

    			if (current_block_type !== (current_block_type = select_block_type(ctx))) {
    				if_block0.d(1);
    				if_block0 = current_block_type(ctx);

    				if (if_block0) {
    					if_block0.c();
    					if_block0.m(div0, t2);
    				}
    			}

    			if (!/*dirty*/ ctx[2] && /*error*/ ctx[1]) {
    				if (if_block1) {
    					if_block1.p(ctx, dirty);
    				} else {
    					if_block1 = create_if_block_1$3(ctx);
    					if_block1.c();
    					if_block1.m(div2, null);
    				}
    			} else if (if_block1) {
    				if_block1.d(1);
    				if_block1 = null;
    			}
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(heading_slot, local);
    			transition_in(fields_slot, local);
    			transition_in(if_block2);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(heading_slot, local);
    			transition_out(fields_slot, local);
    			transition_out(if_block2);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div3);
    			if (heading_slot) heading_slot.d(detaching);
    			if (fields_slot) fields_slot.d(detaching);
    			if_block0.d();
    			if (if_block1) if_block1.d();
    			mounted = false;
    			run_all(dispose);
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
    	const dispatch = createEventDispatcher();
    	let { waiting = false } = $$props;
    	let { error = "" } = $$props;
    	let dirty = false;

    	function submit(event) {
    		$$invalidate(2, dirty = false);
    		dispatch("submit", { elements: event.target.elements });
    	}

    	function cancel() {
    		$$invalidate(2, dirty = false);
    		dispatch("cancel");
    	}

    	function setDirty() {
    		$$invalidate(2, dirty = true);
    	}

    	const writable_props = ["waiting", "error"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<FormTemplate> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("FormTemplate", $$slots, ['heading','fields','default']);

    	$$self.$$set = $$props => {
    		if ("waiting" in $$props) $$invalidate(0, waiting = $$props.waiting);
    		if ("error" in $$props) $$invalidate(1, error = $$props.error);
    		if ("$$scope" in $$props) $$invalidate(6, $$scope = $$props.$$scope);
    	};

    	$$self.$capture_state = () => ({
    		createEventDispatcher,
    		dispatch,
    		waiting,
    		error,
    		dirty,
    		submit,
    		cancel,
    		setDirty
    	});

    	$$self.$inject_state = $$props => {
    		if ("waiting" in $$props) $$invalidate(0, waiting = $$props.waiting);
    		if ("error" in $$props) $$invalidate(1, error = $$props.error);
    		if ("dirty" in $$props) $$invalidate(2, dirty = $$props.dirty);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	return [waiting, error, dirty, submit, cancel, setDirty, $$scope, $$slots];
    }

    class FormTemplate extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$7, create_fragment$7, safe_not_equal, { waiting: 0, error: 1 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "FormTemplate",
    			options,
    			id: create_fragment$7.name
    		});
    	}

    	get waiting() {
    		throw new Error("<FormTemplate>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set waiting(value) {
    		throw new Error("<FormTemplate>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get error() {
    		throw new Error("<FormTemplate>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set error(value) {
    		throw new Error("<FormTemplate>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/common/InputField.svelte generated by Svelte v3.24.1 */

    const file$7 = "src/common/InputField.svelte";

    // (24:8) {:else}
    function create_else_block$4(ctx) {
    	let input;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			input = element("input");
    			input.required = /*required*/ ctx[4];
    			attr_dev(input, "placeholder", /*placeholder*/ ctx[0]);
    			add_location(input, file$7, 24, 8, 604);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, input, anchor);
    			set_input_value(input, /*value*/ ctx[1]);

    			if (!mounted) {
    				dispose = [
    					listen_dev(input, "input", /*handleInputType*/ ctx[6], false, false, false),
    					listen_dev(input, "input", /*input_input_handler*/ ctx[8])
    				];

    				mounted = true;
    			}
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*required*/ 16) {
    				prop_dev(input, "required", /*required*/ ctx[4]);
    			}

    			if (dirty & /*placeholder*/ 1) {
    				attr_dev(input, "placeholder", /*placeholder*/ ctx[0]);
    			}

    			if (dirty & /*value*/ 2 && input.value !== /*value*/ ctx[1]) {
    				set_input_value(input, /*value*/ ctx[1]);
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(input);
    			mounted = false;
    			run_all(dispose);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block$4.name,
    		type: "else",
    		source: "(24:8) {:else}",
    		ctx
    	});

    	return block;
    }

    // (22:8) {#if readonly}
    function create_if_block_1$4(ctx) {
    	let span;
    	let t;

    	const block = {
    		c: function create() {
    			span = element("span");
    			t = text(/*value*/ ctx[1]);
    			attr_dev(span, "class", "readonly svelte-1fkd6hd");
    			add_location(span, file$7, 22, 12, 542);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, span, anchor);
    			append_dev(span, t);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*value*/ 2) set_data_dev(t, /*value*/ ctx[1]);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(span);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_1$4.name,
    		type: "if",
    		source: "(22:8) {#if readonly}",
    		ctx
    	});

    	return block;
    }

    // (30:8) {#if icon}
    function create_if_block$5(ctx) {
    	let i;
    	let i_class_value;

    	const block = {
    		c: function create() {
    			i = element("i");
    			attr_dev(i, "class", i_class_value = "" + (/*icon*/ ctx[2] + " icon" + " svelte-1fkd6hd"));
    			add_location(i, file$7, 29, 18, 753);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, i, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*icon*/ 4 && i_class_value !== (i_class_value = "" + (/*icon*/ ctx[2] + " icon" + " svelte-1fkd6hd"))) {
    				attr_dev(i, "class", i_class_value);
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(i);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$5.name,
    		type: "if",
    		source: "(30:8) {#if icon}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$8(ctx) {
    	let div2;
    	let div1;
    	let div0;
    	let t0;
    	let t1;
    	let t2;
    	let t3;

    	function select_block_type(ctx, dirty) {
    		if (/*readonly*/ ctx[5]) return create_if_block_1$4;
    		return create_else_block$4;
    	}

    	let current_block_type = select_block_type(ctx);
    	let if_block0 = current_block_type(ctx);
    	let if_block1 = /*icon*/ ctx[2] && create_if_block$5(ctx);

    	const block = {
    		c: function create() {
    			div2 = element("div");
    			div1 = element("div");
    			div0 = element("div");
    			t0 = text(/*label*/ ctx[3]);
    			t1 = text(":");
    			t2 = space();
    			if_block0.c();
    			t3 = space();
    			if (if_block1) if_block1.c();
    			attr_dev(div0, "class", "ui label svelte-1fkd6hd");
    			toggle_class(div0, "black", /*readonly*/ ctx[5]);
    			add_location(div0, file$7, 18, 8, 425);
    			attr_dev(div1, "class", "ui labeled right icon input field svelte-1fkd6hd");
    			add_location(div1, file$7, 17, 4, 369);
    			attr_dev(div2, "class", "field");
    			add_location(div2, file$7, 16, 0, 345);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div2, anchor);
    			append_dev(div2, div1);
    			append_dev(div1, div0);
    			append_dev(div0, t0);
    			append_dev(div0, t1);
    			append_dev(div1, t2);
    			if_block0.m(div1, null);
    			append_dev(div1, t3);
    			if (if_block1) if_block1.m(div1, null);
    		},
    		p: function update(ctx, [dirty]) {
    			if (dirty & /*label*/ 8) set_data_dev(t0, /*label*/ ctx[3]);

    			if (dirty & /*readonly*/ 32) {
    				toggle_class(div0, "black", /*readonly*/ ctx[5]);
    			}

    			if (current_block_type === (current_block_type = select_block_type(ctx)) && if_block0) {
    				if_block0.p(ctx, dirty);
    			} else {
    				if_block0.d(1);
    				if_block0 = current_block_type(ctx);

    				if (if_block0) {
    					if_block0.c();
    					if_block0.m(div1, t3);
    				}
    			}

    			if (/*icon*/ ctx[2]) {
    				if (if_block1) {
    					if_block1.p(ctx, dirty);
    				} else {
    					if_block1 = create_if_block$5(ctx);
    					if_block1.c();
    					if_block1.m(div1, null);
    				}
    			} else if (if_block1) {
    				if_block1.d(1);
    				if_block1 = null;
    			}
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div2);
    			if_block0.d();
    			if (if_block1) if_block1.d();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$8.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$8($$self, $$props, $$invalidate) {
    	let { icon = "" } = $$props;
    	let { label = "" } = $$props;
    	let { placeholder = "" } = $$props;
    	let { required = false } = $$props;
    	let { type = "text" } = $$props;
    	let { value = "" } = $$props;
    	let { readonly = false } = $$props;
    	placeholder = placeholder || label;

    	const handleInputType = e => {
    		e.target.type = type;
    	};

    	const writable_props = ["icon", "label", "placeholder", "required", "type", "value", "readonly"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<InputField> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("InputField", $$slots, []);

    	function input_input_handler() {
    		value = this.value;
    		$$invalidate(1, value);
    	}

    	$$self.$$set = $$props => {
    		if ("icon" in $$props) $$invalidate(2, icon = $$props.icon);
    		if ("label" in $$props) $$invalidate(3, label = $$props.label);
    		if ("placeholder" in $$props) $$invalidate(0, placeholder = $$props.placeholder);
    		if ("required" in $$props) $$invalidate(4, required = $$props.required);
    		if ("type" in $$props) $$invalidate(7, type = $$props.type);
    		if ("value" in $$props) $$invalidate(1, value = $$props.value);
    		if ("readonly" in $$props) $$invalidate(5, readonly = $$props.readonly);
    	};

    	$$self.$capture_state = () => ({
    		icon,
    		label,
    		placeholder,
    		required,
    		type,
    		value,
    		readonly,
    		handleInputType
    	});

    	$$self.$inject_state = $$props => {
    		if ("icon" in $$props) $$invalidate(2, icon = $$props.icon);
    		if ("label" in $$props) $$invalidate(3, label = $$props.label);
    		if ("placeholder" in $$props) $$invalidate(0, placeholder = $$props.placeholder);
    		if ("required" in $$props) $$invalidate(4, required = $$props.required);
    		if ("type" in $$props) $$invalidate(7, type = $$props.type);
    		if ("value" in $$props) $$invalidate(1, value = $$props.value);
    		if ("readonly" in $$props) $$invalidate(5, readonly = $$props.readonly);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	return [
    		placeholder,
    		value,
    		icon,
    		label,
    		required,
    		readonly,
    		handleInputType,
    		type,
    		input_input_handler
    	];
    }

    class InputField extends SvelteComponentDev {
    	constructor(options) {
    		super(options);

    		init(this, options, instance$8, create_fragment$8, safe_not_equal, {
    			icon: 2,
    			label: 3,
    			placeholder: 0,
    			required: 4,
    			type: 7,
    			value: 1,
    			readonly: 5
    		});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "InputField",
    			options,
    			id: create_fragment$8.name
    		});
    	}

    	get icon() {
    		throw new Error("<InputField>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set icon(value) {
    		throw new Error("<InputField>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get label() {
    		throw new Error("<InputField>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set label(value) {
    		throw new Error("<InputField>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get placeholder() {
    		throw new Error("<InputField>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set placeholder(value) {
    		throw new Error("<InputField>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get required() {
    		throw new Error("<InputField>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set required(value) {
    		throw new Error("<InputField>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get type() {
    		throw new Error("<InputField>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set type(value) {
    		throw new Error("<InputField>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get value() {
    		throw new Error("<InputField>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set value(value) {
    		throw new Error("<InputField>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get readonly() {
    		throw new Error("<InputField>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set readonly(value) {
    		throw new Error("<InputField>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/common/ArrayField.svelte generated by Svelte v3.24.1 */

    const file$8 = "src/common/ArrayField.svelte";

    function get_each_context$3(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[10] = list[i];
    	child_ctx[12] = i;
    	return child_ctx;
    }

    // (73:20) {:else}
    function create_else_block$5(ctx) {
    	let div;
    	let t0_value = /*item*/ ctx[10] + "";
    	let t0;
    	let t1;
    	let i;
    	let div_data_position_value;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			div = element("div");
    			t0 = text(t0_value);
    			t1 = space();
    			i = element("i");
    			attr_dev(i, "class", "trash icon svelte-1x3vb5m");
    			add_location(i, file$8, 77, 28, 2308);
    			attr_dev(div, "class", "view svelte-1x3vb5m");
    			attr_dev(div, "data-position", div_data_position_value = /*position*/ ctx[12]);
    			add_location(div, file$8, 73, 24, 2120);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			append_dev(div, t0);
    			append_dev(div, t1);
    			append_dev(div, i);

    			if (!mounted) {
    				dispose = [
    					listen_dev(i, "click", /*onDelete*/ ctx[5], false, false, false),
    					listen_dev(div, "click", /*onClickItem*/ ctx[4], false, false, false)
    				];

    				mounted = true;
    			}
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*value*/ 1 && t0_value !== (t0_value = /*item*/ ctx[10] + "")) set_data_dev(t0, t0_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    			mounted = false;
    			run_all(dispose);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block$5.name,
    		type: "else",
    		source: "(73:20) {:else}",
    		ctx
    	});

    	return block;
    }

    // (65:20) {#if position === editPosition}
    function create_if_block$6(ctx) {
    	let div;
    	let input;
    	let input_data_position_value;
    	let input_value_value;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			div = element("div");
    			input = element("input");
    			attr_dev(input, "data-position", input_data_position_value = /*position*/ ctx[12]);
    			input.value = input_value_value = /*item*/ ctx[10];
    			input.autofocus = true;
    			attr_dev(input, "class", "svelte-1x3vb5m");
    			add_location(input, file$8, 66, 28, 1798);
    			attr_dev(div, "class", "edit svelte-1x3vb5m");
    			add_location(div, file$8, 65, 24, 1751);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			append_dev(div, input);
    			input.focus();

    			if (!mounted) {
    				dispose = [
    					listen_dev(input, "keydown", /*handleKey*/ ctx[8], false, false, false),
    					listen_dev(input, "blur", /*saveEdit*/ ctx[7], false, false, false)
    				];

    				mounted = true;
    			}
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*value*/ 1 && input_value_value !== (input_value_value = /*item*/ ctx[10]) && input.value !== input_value_value) {
    				prop_dev(input, "value", input_value_value);
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    			mounted = false;
    			run_all(dispose);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$6.name,
    		type: "if",
    		source: "(65:20) {#if position === editPosition}",
    		ctx
    	});

    	return block;
    }

    // (63:12) {#each (value || []) as item, position}
    function create_each_block$3(ctx) {
    	let div;

    	function select_block_type(ctx, dirty) {
    		if (/*position*/ ctx[12] === /*editPosition*/ ctx[2]) return create_if_block$6;
    		return create_else_block$5;
    	}

    	let current_block_type = select_block_type(ctx);
    	let if_block = current_block_type(ctx);

    	const block = {
    		c: function create() {
    			div = element("div");
    			if_block.c();
    			attr_dev(div, "class", "item svelte-1x3vb5m");
    			add_location(div, file$8, 63, 16, 1656);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			if_block.m(div, null);
    		},
    		p: function update(ctx, dirty) {
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
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    			if_block.d();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block$3.name,
    		type: "each",
    		source: "(63:12) {#each (value || []) as item, position}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$9(ctx) {
    	let div5;
    	let div4;
    	let div0;
    	let t0;
    	let t1;
    	let t2;
    	let div3;
    	let t3;
    	let div2;
    	let div1;
    	let t4;
    	let i;
    	let t5;
    	let div11;
    	let div6;
    	let t6_value = /*value*/ ctx[0][/*removePosition*/ ctx[3]] + "";
    	let t6;
    	let t7;
    	let div7;
    	let p;
    	let t8;
    	let br;
    	let t9;
    	let div10;
    	let div8;
    	let t11;
    	let div9;
    	let mounted;
    	let dispose;
    	let each_value = /*value*/ ctx[0] || [];
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block$3(get_each_context$3(ctx, each_value, i));
    	}

    	const block = {
    		c: function create() {
    			div5 = element("div");
    			div4 = element("div");
    			div0 = element("div");
    			t0 = text(/*label*/ ctx[1]);
    			t1 = text(":");
    			t2 = space();
    			div3 = element("div");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			t3 = space();
    			div2 = element("div");
    			div1 = element("div");
    			t4 = text("Add another item\n                    ");
    			i = element("i");
    			t5 = space();
    			div11 = element("div");
    			div6 = element("div");
    			t6 = text(t6_value);
    			t7 = space();
    			div7 = element("div");
    			p = element("p");
    			t8 = text("Are you should you want to remove?");
    			br = element("br");
    			t9 = space();
    			div10 = element("div");
    			div8 = element("div");
    			div8.textContent = "Yes, remove.";
    			t11 = space();
    			div9 = element("div");
    			div9.textContent = "Cancel, keep.";
    			attr_dev(div0, "class", "ui label svelte-1x3vb5m");
    			add_location(div0, file$8, 58, 8, 1501);
    			attr_dev(i, "class", "circle plus icon svelte-1x3vb5m");
    			add_location(i, file$8, 85, 20, 2594);
    			attr_dev(div1, "class", "add svelte-1x3vb5m");
    			add_location(div1, file$8, 83, 16, 2502);
    			attr_dev(div2, "class", "item svelte-1x3vb5m");
    			add_location(div2, file$8, 82, 12, 2467);
    			attr_dev(div3, "class", "array svelte-1x3vb5m");
    			add_location(div3, file$8, 61, 8, 1568);
    			attr_dev(div4, "class", "ui labeled right input");
    			add_location(div4, file$8, 57, 4, 1456);
    			attr_dev(div5, "class", "field");
    			add_location(div5, file$8, 56, 0, 1432);
    			attr_dev(div6, "class", "header");
    			add_location(div6, file$8, 93, 4, 2752);
    			add_location(br, file$8, 96, 46, 2886);
    			add_location(p, file$8, 95, 8, 2836);
    			attr_dev(div7, "class", "content");
    			add_location(div7, file$8, 94, 4, 2806);
    			attr_dev(div8, "class", "ui approve positive button");
    			add_location(div8, file$8, 100, 8, 2950);
    			attr_dev(div9, "class", "ui cancel negative button");
    			add_location(div9, file$8, 101, 8, 3017);
    			attr_dev(div10, "class", "actions");
    			add_location(div10, file$8, 99, 4, 2920);
    			attr_dev(div11, "id", "remove-item");
    			attr_dev(div11, "class", "ui tiny modal");
    			add_location(div11, file$8, 92, 0, 2703);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div5, anchor);
    			append_dev(div5, div4);
    			append_dev(div4, div0);
    			append_dev(div0, t0);
    			append_dev(div0, t1);
    			append_dev(div4, t2);
    			append_dev(div4, div3);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(div3, null);
    			}

    			append_dev(div3, t3);
    			append_dev(div3, div2);
    			append_dev(div2, div1);
    			append_dev(div1, t4);
    			append_dev(div1, i);
    			insert_dev(target, t5, anchor);
    			insert_dev(target, div11, anchor);
    			append_dev(div11, div6);
    			append_dev(div6, t6);
    			append_dev(div11, t7);
    			append_dev(div11, div7);
    			append_dev(div7, p);
    			append_dev(p, t8);
    			append_dev(p, br);
    			append_dev(div11, t9);
    			append_dev(div11, div10);
    			append_dev(div10, div8);
    			append_dev(div10, t11);
    			append_dev(div10, div9);

    			if (!mounted) {
    				dispose = listen_dev(div1, "click", /*onAdd*/ ctx[6], false, false, false);
    				mounted = true;
    			}
    		},
    		p: function update(ctx, [dirty]) {
    			if (dirty & /*label*/ 2) set_data_dev(t0, /*label*/ ctx[1]);

    			if (dirty & /*value, handleKey, saveEdit, editPosition, onClickItem, onDelete*/ 437) {
    				each_value = /*value*/ ctx[0] || [];
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context$3(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block$3(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(div3, t3);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value.length;
    			}

    			if (dirty & /*value, removePosition*/ 9 && t6_value !== (t6_value = /*value*/ ctx[0][/*removePosition*/ ctx[3]] + "")) set_data_dev(t6, t6_value);
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div5);
    			destroy_each(each_blocks, detaching);
    			if (detaching) detach_dev(t5);
    			if (detaching) detach_dev(div11);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$9.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$9($$self, $$props, $$invalidate) {
    	let { label } = $$props;
    	let { value = [] } = $$props;
    	let editPosition = null;
    	let removePosition = null;

    	const onClickItem = event => {
    		$$invalidate(2, editPosition = parseInt(event.target.dataset.position));
    	};

    	const onDelete = event => {
    		$$invalidate(3, removePosition = parseInt(event.target.parentNode.dataset.position));

    		window.$("#remove-item").modal({
    			onApprove() {
    				$$invalidate(0, value = value.filter((_, index) => index !== removePosition));
    			}
    		}).modal("show");
    	};

    	const onAdd = () => {
    		$$invalidate(0, value = [...value, ""]);
    		$$invalidate(2, editPosition = value.length - 1);
    	};

    	const clearEdit = () => {
    		if (editPosition === value.length - 1) {
    			if (!value[editPosition]) {
    				$$invalidate(0, value = value.filter((_, index) => index !== editPosition));
    			}
    		}

    		$$invalidate(2, editPosition = null);
    	};

    	const saveEdit = event => {
    		if (event.target.value) {
    			$$invalidate(0, value[editPosition] = event.target.value, value);
    		} else {
    			$$invalidate(0, value = value.filter((_, index) => index !== editPosition));
    		}

    		$$invalidate(2, editPosition = null);
    	};

    	const handleKey = event => {
    		if (event.code === "Escape") {
    			clearEdit();
    		} else if (event.code === "Enter") {
    			event.preventDefault();
    			saveEdit(event);
    			return false;
    		}
    	};

    	const writable_props = ["label", "value"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<ArrayField> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("ArrayField", $$slots, []);

    	$$self.$$set = $$props => {
    		if ("label" in $$props) $$invalidate(1, label = $$props.label);
    		if ("value" in $$props) $$invalidate(0, value = $$props.value);
    	};

    	$$self.$capture_state = () => ({
    		label,
    		value,
    		editPosition,
    		removePosition,
    		onClickItem,
    		onDelete,
    		onAdd,
    		clearEdit,
    		saveEdit,
    		handleKey
    	});

    	$$self.$inject_state = $$props => {
    		if ("label" in $$props) $$invalidate(1, label = $$props.label);
    		if ("value" in $$props) $$invalidate(0, value = $$props.value);
    		if ("editPosition" in $$props) $$invalidate(2, editPosition = $$props.editPosition);
    		if ("removePosition" in $$props) $$invalidate(3, removePosition = $$props.removePosition);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	return [
    		value,
    		label,
    		editPosition,
    		removePosition,
    		onClickItem,
    		onDelete,
    		onAdd,
    		saveEdit,
    		handleKey
    	];
    }

    class ArrayField extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$9, create_fragment$9, safe_not_equal, { label: 1, value: 0 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "ArrayField",
    			options,
    			id: create_fragment$9.name
    		});

    		const { ctx } = this.$$;
    		const props = options.props || {};

    		if (/*label*/ ctx[1] === undefined && !("label" in props)) {
    			console.warn("<ArrayField> was created without expected prop 'label'");
    		}
    	}

    	get label() {
    		throw new Error("<ArrayField>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set label(value) {
    		throw new Error("<ArrayField>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get value() {
    		throw new Error("<ArrayField>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set value(value) {
    		throw new Error("<ArrayField>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/common/SelectField.svelte generated by Svelte v3.24.1 */

    const { Object: Object_1$3 } = globals;
    const file$9 = "src/common/SelectField.svelte";

    function get_each_context$4(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[11] = list[i][0];
    	child_ctx[2] = list[i][1];
    	return child_ctx;
    }

    // (41:8) {#if label}
    function create_if_block$7(ctx) {
    	let div;
    	let t0;
    	let t1;

    	const block = {
    		c: function create() {
    			div = element("div");
    			t0 = text(/*label*/ ctx[3]);
    			t1 = text(":");
    			attr_dev(div, "class", "ui label svelte-vpehuf");
    			add_location(div, file$9, 41, 12, 998);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			append_dev(div, t0);
    			append_dev(div, t1);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*label*/ 8) set_data_dev(t0, /*label*/ ctx[3]);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$7.name,
    		type: "if",
    		source: "(41:8) {#if label}",
    		ctx
    	});

    	return block;
    }

    // (51:16) {#each Object.entries(options || {}) as [item, display]}
    function create_each_block$4(ctx) {
    	let div;
    	let t0_value = /*display*/ ctx[2] + "";
    	let t0;
    	let t1;
    	let div_data_value_value;

    	const block = {
    		c: function create() {
    			div = element("div");
    			t0 = text(t0_value);
    			t1 = space();
    			attr_dev(div, "class", "item");
    			attr_dev(div, "data-value", div_data_value_value = /*item*/ ctx[11]);
    			add_location(div, file$9, 51, 20, 1447);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			append_dev(div, t0);
    			append_dev(div, t1);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*options*/ 16 && t0_value !== (t0_value = /*display*/ ctx[2] + "")) set_data_dev(t0, t0_value);

    			if (dirty & /*options*/ 16 && div_data_value_value !== (div_data_value_value = /*item*/ ctx[11])) {
    				attr_dev(div, "data-value", div_data_value_value);
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block$4.name,
    		type: "each",
    		source: "(51:16) {#each Object.entries(options || {}) as [item, display]}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$a(ctx) {
    	let div4;
    	let div3;
    	let t0;
    	let div2;
    	let input;
    	let t1;
    	let i;
    	let t2;
    	let div0;
    	let t3;
    	let t4;
    	let div1;
    	let mounted;
    	let dispose;
    	let if_block = /*label*/ ctx[3] && create_if_block$7(ctx);
    	let each_value = Object.entries(/*options*/ ctx[4] || {});
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block$4(get_each_context$4(ctx, each_value, i));
    	}

    	const block = {
    		c: function create() {
    			div4 = element("div");
    			div3 = element("div");
    			if (if_block) if_block.c();
    			t0 = space();
    			div2 = element("div");
    			input = element("input");
    			t1 = space();
    			i = element("i");
    			t2 = space();
    			div0 = element("div");
    			t3 = text(/*placeholder*/ ctx[1]);
    			t4 = space();
    			div1 = element("div");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			attr_dev(input, "type", "hidden");
    			input.value = /*value*/ ctx[0];
    			add_location(input, file$9, 46, 12, 1163);
    			attr_dev(i, "class", "dropdown icon");
    			add_location(i, file$9, 47, 12, 1235);
    			attr_dev(div0, "class", "default text");
    			add_location(div0, file$9, 48, 12, 1277);
    			attr_dev(div1, "class", "menu");
    			add_location(div1, file$9, 49, 12, 1335);
    			attr_dev(div2, "class", "ui search selection dropdown");
    			add_location(div2, file$9, 45, 8, 1087);
    			attr_dev(div3, "class", "ui right icon input");
    			toggle_class(div3, "labeled", /*label*/ ctx[3]);
    			add_location(div3, file$9, 39, 4, 910);
    			attr_dev(div4, "class", "field");
    			add_location(div4, file$9, 38, 0, 886);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div4, anchor);
    			append_dev(div4, div3);
    			if (if_block) if_block.m(div3, null);
    			append_dev(div3, t0);
    			append_dev(div3, div2);
    			append_dev(div2, input);
    			append_dev(div2, t1);
    			append_dev(div2, i);
    			append_dev(div2, t2);
    			append_dev(div2, div0);
    			append_dev(div0, t3);
    			append_dev(div2, t4);
    			append_dev(div2, div1);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(div1, null);
    			}

    			/*div2_binding*/ ctx[8](div2);

    			if (!mounted) {
    				dispose = listen_dev(input, "change", /*updateValue*/ ctx[6], false, false, false);
    				mounted = true;
    			}
    		},
    		p: function update(ctx, [dirty]) {
    			if (/*label*/ ctx[3]) {
    				if (if_block) {
    					if_block.p(ctx, dirty);
    				} else {
    					if_block = create_if_block$7(ctx);
    					if_block.c();
    					if_block.m(div3, t0);
    				}
    			} else if (if_block) {
    				if_block.d(1);
    				if_block = null;
    			}

    			if (dirty & /*value*/ 1) {
    				prop_dev(input, "value", /*value*/ ctx[0]);
    			}

    			if (dirty & /*placeholder*/ 2) set_data_dev(t3, /*placeholder*/ ctx[1]);

    			if (dirty & /*Object, options*/ 16) {
    				each_value = Object.entries(/*options*/ ctx[4] || {});
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context$4(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block$4(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(div1, null);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value.length;
    			}

    			if (dirty & /*label*/ 8) {
    				toggle_class(div3, "labeled", /*label*/ ctx[3]);
    			}
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div4);
    			if (if_block) if_block.d();
    			destroy_each(each_blocks, detaching);
    			/*div2_binding*/ ctx[8](null);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$a.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$a($$self, $$props, $$invalidate) {
    	const dispatch = createEventDispatcher();
    	let { name = null } = $$props;
    	let { label = false } = $$props;
    	let { options = {} } = $$props;
    	let { value = "" } = $$props;
    	let { placeholder = "" } = $$props;
    	let { display = "" } = $$props;
    	let dropdown = null;
    	placeholder = placeholder || label;

    	const updateValue = event => {
    		$$invalidate(0, value = event.target.value);
    		$$invalidate(2, display = options[value]);
    		dispatch("change", { name, value });
    	};

    	onMount(() => {
    		updateDropdown();
    	});

    	const updateDropdown = () => {
    		if (value !== null) {
    			window.$(dropdown).dropdown("set selected", value);
    		} else {
    			window.$(dropdown).dropdown("restore defaults preventChangeTrigger");
    		}
    	};

    	const writable_props = ["name", "label", "options", "value", "placeholder", "display"];

    	Object_1$3.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<SelectField> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("SelectField", $$slots, []);

    	function div2_binding($$value) {
    		binding_callbacks[$$value ? "unshift" : "push"](() => {
    			dropdown = $$value;
    			$$invalidate(5, dropdown);
    		});
    	}

    	$$self.$$set = $$props => {
    		if ("name" in $$props) $$invalidate(7, name = $$props.name);
    		if ("label" in $$props) $$invalidate(3, label = $$props.label);
    		if ("options" in $$props) $$invalidate(4, options = $$props.options);
    		if ("value" in $$props) $$invalidate(0, value = $$props.value);
    		if ("placeholder" in $$props) $$invalidate(1, placeholder = $$props.placeholder);
    		if ("display" in $$props) $$invalidate(2, display = $$props.display);
    	};

    	$$self.$capture_state = () => ({
    		onMount,
    		createEventDispatcher,
    		dispatch,
    		name,
    		label,
    		options,
    		value,
    		placeholder,
    		display,
    		dropdown,
    		updateValue,
    		updateDropdown
    	});

    	$$self.$inject_state = $$props => {
    		if ("name" in $$props) $$invalidate(7, name = $$props.name);
    		if ("label" in $$props) $$invalidate(3, label = $$props.label);
    		if ("options" in $$props) $$invalidate(4, options = $$props.options);
    		if ("value" in $$props) $$invalidate(0, value = $$props.value);
    		if ("placeholder" in $$props) $$invalidate(1, placeholder = $$props.placeholder);
    		if ("display" in $$props) $$invalidate(2, display = $$props.display);
    		if ("dropdown" in $$props) $$invalidate(5, dropdown = $$props.dropdown);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*value*/ 1) {
    			 updateDropdown();
    		}
    	};

    	return [
    		value,
    		placeholder,
    		display,
    		label,
    		options,
    		dropdown,
    		updateValue,
    		name,
    		div2_binding
    	];
    }

    class SelectField extends SvelteComponentDev {
    	constructor(options) {
    		super(options);

    		init(this, options, instance$a, create_fragment$a, safe_not_equal, {
    			name: 7,
    			label: 3,
    			options: 4,
    			value: 0,
    			placeholder: 1,
    			display: 2
    		});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "SelectField",
    			options,
    			id: create_fragment$a.name
    		});
    	}

    	get name() {
    		throw new Error("<SelectField>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set name(value) {
    		throw new Error("<SelectField>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get label() {
    		throw new Error("<SelectField>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set label(value) {
    		throw new Error("<SelectField>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get options() {
    		throw new Error("<SelectField>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set options(value) {
    		throw new Error("<SelectField>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get value() {
    		throw new Error("<SelectField>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set value(value) {
    		throw new Error("<SelectField>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get placeholder() {
    		throw new Error("<SelectField>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set placeholder(value) {
    		throw new Error("<SelectField>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get display() {
    		throw new Error("<SelectField>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set display(value) {
    		throw new Error("<SelectField>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/views/NodeEdit.svelte generated by Svelte v3.24.1 */
    const file$a = "src/views/NodeEdit.svelte";

    function get_each_context$5(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[12] = list[i];
    	child_ctx[13] = list;
    	child_ctx[14] = i;
    	return child_ctx;
    }

    // (103:0) {:else}
    function create_else_block_1$2(ctx) {
    	let div1;
    	let div0;

    	const block = {
    		c: function create() {
    			div1 = element("div");
    			div0 = element("div");
    			div0.textContent = "Loading";
    			attr_dev(div0, "class", "ui text loader");
    			add_location(div0, file$a, 104, 8, 3260);
    			attr_dev(div1, "class", "ui active inverted dimmer");
    			add_location(div1, file$a, 103, 4, 3212);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div1, anchor);
    			append_dev(div1, div0);
    		},
    		p: noop,
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div1);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block_1$2.name,
    		type: "else",
    		source: "(103:0) {:else}",
    		ctx
    	});

    	return block;
    }

    // (61:0) {#if edit}
    function create_if_block$8(ctx) {
    	let formtemplate;
    	let current;

    	formtemplate = new FormTemplate({
    			props: {
    				error: /*error*/ ctx[1],
    				waiting: /*waiting*/ ctx[2],
    				$$slots: {
    					default: [create_default_slot],
    					fields: [create_fields_slot],
    					heading: [create_heading_slot]
    				},
    				$$scope: { ctx }
    			},
    			$$inline: true
    		});

    	formtemplate.$on("cancel", /*cancel*/ ctx[5]);
    	formtemplate.$on("submit", /*submit*/ ctx[4]);

    	const block = {
    		c: function create() {
    			create_component(formtemplate.$$.fragment);
    		},
    		m: function mount(target, anchor) {
    			mount_component(formtemplate, target, anchor);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			const formtemplate_changes = {};
    			if (dirty & /*error*/ 2) formtemplate_changes.error = /*error*/ ctx[1];
    			if (dirty & /*waiting*/ 4) formtemplate_changes.waiting = /*waiting*/ ctx[2];

    			if (dirty & /*$$scope, edit*/ 32769) {
    				formtemplate_changes.$$scope = { dirty, ctx };
    			}

    			formtemplate.$set(formtemplate_changes);
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(formtemplate.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(formtemplate.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			destroy_component(formtemplate, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$8.name,
    		type: "if",
    		source: "(61:0) {#if edit}",
    		ctx
    	});

    	return block;
    }

    // (66:8) <span slot="heading">
    function create_heading_slot(ctx) {
    	let span;
    	let t_value = /*edit*/ ctx[0].title + "";
    	let t;

    	const block = {
    		c: function create() {
    			span = element("span");
    			t = text(t_value);
    			attr_dev(span, "slot", "heading");
    			add_location(span, file$a, 65, 8, 1915);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, span, anchor);
    			append_dev(span, t);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*edit*/ 1 && t_value !== (t_value = /*edit*/ ctx[0].title + "")) set_data_dev(t, t_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(span);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_heading_slot.name,
    		type: "slot",
    		source: "(66:8) <span slot=\\\"heading\\\">",
    		ctx
    	});

    	return block;
    }

    // (75:12) {:else}
    function create_else_block$6(ctx) {
    	let inputfield;
    	let current;

    	inputfield = new InputField({
    			props: {
    				label: "Label",
    				readonly: "true",
    				value: /*edit*/ ctx[0].label
    			},
    			$$inline: true
    		});

    	const block = {
    		c: function create() {
    			create_component(inputfield.$$.fragment);
    		},
    		m: function mount(target, anchor) {
    			mount_component(inputfield, target, anchor);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			const inputfield_changes = {};
    			if (dirty & /*edit*/ 1) inputfield_changes.value = /*edit*/ ctx[0].label;
    			inputfield.$set(inputfield_changes);
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(inputfield.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(inputfield.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			destroy_component(inputfield, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block$6.name,
    		type: "else",
    		source: "(75:12) {:else}",
    		ctx
    	});

    	return block;
    }

    // (69:12) {#if edit.isNew}
    function create_if_block_3$1(ctx) {
    	let selectfield;
    	let updating_value;
    	let current;

    	function selectfield_value_binding(value) {
    		/*selectfield_value_binding*/ ctx[7].call(null, value);
    	}

    	let selectfield_props = {
    		label: "Label",
    		options: /*schema*/ ctx[3].labelOptions
    	};

    	if (/*edit*/ ctx[0].label !== void 0) {
    		selectfield_props.value = /*edit*/ ctx[0].label;
    	}

    	selectfield = new SelectField({ props: selectfield_props, $$inline: true });
    	binding_callbacks.push(() => bind(selectfield, "value", selectfield_value_binding));

    	const block = {
    		c: function create() {
    			create_component(selectfield.$$.fragment);
    		},
    		m: function mount(target, anchor) {
    			mount_component(selectfield, target, anchor);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			const selectfield_changes = {};

    			if (!updating_value && dirty & /*edit*/ 1) {
    				updating_value = true;
    				selectfield_changes.value = /*edit*/ ctx[0].label;
    				add_flush_callback(() => updating_value = false);
    			}

    			selectfield.$set(selectfield_changes);
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(selectfield.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(selectfield.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			destroy_component(selectfield, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_3$1.name,
    		type: "if",
    		source: "(69:12) {#if edit.isNew}",
    		ctx
    	});

    	return block;
    }

    // (93:54) 
    function create_if_block_2$2(ctx) {
    	let inputfield;
    	let updating_value;
    	let current;

    	function inputfield_value_binding_1(value) {
    		/*inputfield_value_binding_1*/ ctx[10].call(null, value, /*attribute*/ ctx[12]);
    	}

    	let inputfield_props = {
    		label: /*attribute*/ ctx[12].title,
    		required: /*attribute*/ ctx[12].required
    	};

    	if (/*edit*/ ctx[0].data[/*attribute*/ ctx[12].name] !== void 0) {
    		inputfield_props.value = /*edit*/ ctx[0].data[/*attribute*/ ctx[12].name];
    	}

    	inputfield = new InputField({ props: inputfield_props, $$inline: true });
    	binding_callbacks.push(() => bind(inputfield, "value", inputfield_value_binding_1));

    	const block = {
    		c: function create() {
    			create_component(inputfield.$$.fragment);
    		},
    		m: function mount(target, anchor) {
    			mount_component(inputfield, target, anchor);
    			current = true;
    		},
    		p: function update(new_ctx, dirty) {
    			ctx = new_ctx;
    			const inputfield_changes = {};
    			if (dirty & /*edit*/ 1) inputfield_changes.label = /*attribute*/ ctx[12].title;
    			if (dirty & /*edit*/ 1) inputfield_changes.required = /*attribute*/ ctx[12].required;

    			if (!updating_value && dirty & /*edit*/ 1) {
    				updating_value = true;
    				inputfield_changes.value = /*edit*/ ctx[0].data[/*attribute*/ ctx[12].name];
    				add_flush_callback(() => updating_value = false);
    			}

    			inputfield.$set(inputfield_changes);
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(inputfield.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(inputfield.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			destroy_component(inputfield, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_2$2.name,
    		type: "if",
    		source: "(93:54) ",
    		ctx
    	});

    	return block;
    }

    // (88:16) {#if attribute.type === "array"}
    function create_if_block_1$5(ctx) {
    	let arrayfield;
    	let updating_value;
    	let current;

    	function arrayfield_value_binding(value) {
    		/*arrayfield_value_binding*/ ctx[9].call(null, value, /*attribute*/ ctx[12]);
    	}

    	let arrayfield_props = { label: /*attribute*/ ctx[12].title };

    	if (/*edit*/ ctx[0].data[/*attribute*/ ctx[12].name] !== void 0) {
    		arrayfield_props.value = /*edit*/ ctx[0].data[/*attribute*/ ctx[12].name];
    	}

    	arrayfield = new ArrayField({ props: arrayfield_props, $$inline: true });
    	binding_callbacks.push(() => bind(arrayfield, "value", arrayfield_value_binding));

    	const block = {
    		c: function create() {
    			create_component(arrayfield.$$.fragment);
    		},
    		m: function mount(target, anchor) {
    			mount_component(arrayfield, target, anchor);
    			current = true;
    		},
    		p: function update(new_ctx, dirty) {
    			ctx = new_ctx;
    			const arrayfield_changes = {};
    			if (dirty & /*edit*/ 1) arrayfield_changes.label = /*attribute*/ ctx[12].title;

    			if (!updating_value && dirty & /*edit*/ 1) {
    				updating_value = true;
    				arrayfield_changes.value = /*edit*/ ctx[0].data[/*attribute*/ ctx[12].name];
    				add_flush_callback(() => updating_value = false);
    			}

    			arrayfield.$set(arrayfield_changes);
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(arrayfield.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(arrayfield.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			destroy_component(arrayfield, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_1$5.name,
    		type: "if",
    		source: "(88:16) {#if attribute.type === \\\"array\\\"}",
    		ctx
    	});

    	return block;
    }

    // (87:12) {#each edit.attributes as attribute}
    function create_each_block$5(ctx) {
    	let current_block_type_index;
    	let if_block;
    	let if_block_anchor;
    	let current;
    	const if_block_creators = [create_if_block_1$5, create_if_block_2$2];
    	const if_blocks = [];

    	function select_block_type_2(ctx, dirty) {
    		if (/*attribute*/ ctx[12].type === "array") return 0;
    		if (/*attribute*/ ctx[12].type === "string") return 1;
    		return -1;
    	}

    	if (~(current_block_type_index = select_block_type_2(ctx))) {
    		if_block = if_blocks[current_block_type_index] = if_block_creators[current_block_type_index](ctx);
    	}

    	const block = {
    		c: function create() {
    			if (if_block) if_block.c();
    			if_block_anchor = empty();
    		},
    		m: function mount(target, anchor) {
    			if (~current_block_type_index) {
    				if_blocks[current_block_type_index].m(target, anchor);
    			}

    			insert_dev(target, if_block_anchor, anchor);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			let previous_block_index = current_block_type_index;
    			current_block_type_index = select_block_type_2(ctx);

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
    					if_block.m(if_block_anchor.parentNode, if_block_anchor);
    				} else {
    					if_block = null;
    				}
    			}
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(if_block);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(if_block);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (~current_block_type_index) {
    				if_blocks[current_block_type_index].d(detaching);
    			}

    			if (detaching) detach_dev(if_block_anchor);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block$5.name,
    		type: "each",
    		source: "(87:12) {#each edit.attributes as attribute}",
    		ctx
    	});

    	return block;
    }

    // (68:8) <div slot="fields">
    function create_fields_slot(ctx) {
    	let div;
    	let current_block_type_index;
    	let if_block;
    	let t0;
    	let inputfield;
    	let updating_value;
    	let t1;
    	let current;
    	const if_block_creators = [create_if_block_3$1, create_else_block$6];
    	const if_blocks = [];

    	function select_block_type_1(ctx, dirty) {
    		if (/*edit*/ ctx[0].isNew) return 0;
    		return 1;
    	}

    	current_block_type_index = select_block_type_1(ctx);
    	if_block = if_blocks[current_block_type_index] = if_block_creators[current_block_type_index](ctx);

    	function inputfield_value_binding(value) {
    		/*inputfield_value_binding*/ ctx[8].call(null, value);
    	}

    	let inputfield_props = {
    		label: "Name",
    		readonly: !/*edit*/ ctx[0].isNew
    	};

    	if (/*edit*/ ctx[0].name !== void 0) {
    		inputfield_props.value = /*edit*/ ctx[0].name;
    	}

    	inputfield = new InputField({ props: inputfield_props, $$inline: true });
    	binding_callbacks.push(() => bind(inputfield, "value", inputfield_value_binding));
    	let each_value = /*edit*/ ctx[0].attributes;
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block$5(get_each_context$5(ctx, each_value, i));
    	}

    	const out = i => transition_out(each_blocks[i], 1, 1, () => {
    		each_blocks[i] = null;
    	});

    	const block = {
    		c: function create() {
    			div = element("div");
    			if_block.c();
    			t0 = space();
    			create_component(inputfield.$$.fragment);
    			t1 = space();

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			attr_dev(div, "slot", "fields");
    			add_location(div, file$a, 67, 8, 1965);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			if_blocks[current_block_type_index].m(div, null);
    			append_dev(div, t0);
    			mount_component(inputfield, div, null);
    			append_dev(div, t1);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(div, null);
    			}

    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			let previous_block_index = current_block_type_index;
    			current_block_type_index = select_block_type_1(ctx);

    			if (current_block_type_index === previous_block_index) {
    				if_blocks[current_block_type_index].p(ctx, dirty);
    			} else {
    				group_outros();

    				transition_out(if_blocks[previous_block_index], 1, 1, () => {
    					if_blocks[previous_block_index] = null;
    				});

    				check_outros();
    				if_block = if_blocks[current_block_type_index];

    				if (!if_block) {
    					if_block = if_blocks[current_block_type_index] = if_block_creators[current_block_type_index](ctx);
    					if_block.c();
    				}

    				transition_in(if_block, 1);
    				if_block.m(div, t0);
    			}

    			const inputfield_changes = {};
    			if (dirty & /*edit*/ 1) inputfield_changes.readonly = !/*edit*/ ctx[0].isNew;

    			if (!updating_value && dirty & /*edit*/ 1) {
    				updating_value = true;
    				inputfield_changes.value = /*edit*/ ctx[0].name;
    				add_flush_callback(() => updating_value = false);
    			}

    			inputfield.$set(inputfield_changes);

    			if (dirty & /*edit*/ 1) {
    				each_value = /*edit*/ ctx[0].attributes;
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context$5(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    						transition_in(each_blocks[i], 1);
    					} else {
    						each_blocks[i] = create_each_block$5(child_ctx);
    						each_blocks[i].c();
    						transition_in(each_blocks[i], 1);
    						each_blocks[i].m(div, null);
    					}
    				}

    				group_outros();

    				for (i = each_value.length; i < each_blocks.length; i += 1) {
    					out(i);
    				}

    				check_outros();
    			}
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(if_block);
    			transition_in(inputfield.$$.fragment, local);

    			for (let i = 0; i < each_value.length; i += 1) {
    				transition_in(each_blocks[i]);
    			}

    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(if_block);
    			transition_out(inputfield.$$.fragment, local);
    			each_blocks = each_blocks.filter(Boolean);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				transition_out(each_blocks[i]);
    			}

    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    			if_blocks[current_block_type_index].d();
    			destroy_component(inputfield);
    			destroy_each(each_blocks, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fields_slot.name,
    		type: "slot",
    		source: "(68:8) <div slot=\\\"fields\\\">",
    		ctx
    	});

    	return block;
    }

    // (62:4) <FormTemplate error={error}                   waiting={waiting}                   on:cancel={cancel}                   on:submit={submit}>
    function create_default_slot(ctx) {
    	let t;

    	const block = {
    		c: function create() {
    			t = space();
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, t, anchor);
    		},
    		p: noop,
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(t);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_default_slot.name,
    		type: "slot",
    		source: "(62:4) <FormTemplate error={error}                   waiting={waiting}                   on:cancel={cancel}                   on:submit={submit}>",
    		ctx
    	});

    	return block;
    }

    function create_fragment$b(ctx) {
    	let current_block_type_index;
    	let if_block;
    	let if_block_anchor;
    	let current;
    	const if_block_creators = [create_if_block$8, create_else_block_1$2];
    	const if_blocks = [];

    	function select_block_type(ctx, dirty) {
    		if (/*edit*/ ctx[0]) return 0;
    		return 1;
    	}

    	current_block_type_index = select_block_type(ctx);
    	if_block = if_blocks[current_block_type_index] = if_block_creators[current_block_type_index](ctx);

    	const block = {
    		c: function create() {
    			if_block.c();
    			if_block_anchor = empty();
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			if_blocks[current_block_type_index].m(target, anchor);
    			insert_dev(target, if_block_anchor, anchor);
    			current = true;
    		},
    		p: function update(ctx, [dirty]) {
    			let previous_block_index = current_block_type_index;
    			current_block_type_index = select_block_type(ctx);

    			if (current_block_type_index === previous_block_index) {
    				if_blocks[current_block_type_index].p(ctx, dirty);
    			} else {
    				group_outros();

    				transition_out(if_blocks[previous_block_index], 1, 1, () => {
    					if_blocks[previous_block_index] = null;
    				});

    				check_outros();
    				if_block = if_blocks[current_block_type_index];

    				if (!if_block) {
    					if_block = if_blocks[current_block_type_index] = if_block_creators[current_block_type_index](ctx);
    					if_block.c();
    				}

    				transition_in(if_block, 1);
    				if_block.m(if_block_anchor.parentNode, if_block_anchor);
    			}
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(if_block);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(if_block);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if_blocks[current_block_type_index].d(detaching);
    			if (detaching) detach_dev(if_block_anchor);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$b.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$b($$self, $$props, $$invalidate) {
    	let { params = {} } = $$props;
    	const manager = new RequestManager();
    	const schema = Schema.instance();
    	let edit = null;
    	let error = "";
    	let waiting = false;

    	onMount(async () => {
    		let entity;

    		if (params.key) {
    			entity = await manager.getNode(params.key);
    		} else {
    			entity = new Entity({ label: params.label, name: "" });
    		}

    		if (entity) {
    			$$invalidate(0, edit = entity ? new Edit(entity, schema) : null);
    			document.title = edit.title;
    		} else {
    			toastFail(`Failed to load: ${params.key}`);
    			await pop();
    		}
    	});

    	const submit = async () => {
    		$$invalidate(2, waiting = true);
    		const success = await manager.saveEntity(edit.entity);
    		toastOnCondition(success, `Save ${edit.title}: ${edit.name}`);

    		if (success) {
    			await push("/detail/" + success.key);
    		} else {
    			$$invalidate(1, error = "Save failed, please check logs");
    			$$invalidate(2, waiting = false);
    		}
    	};

    	const cancel = async () => {
    		toastClear();
    		await push("/detail/" + edit.key);
    	};

    	const writable_props = ["params"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<NodeEdit> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("NodeEdit", $$slots, []);

    	function selectfield_value_binding(value) {
    		edit.label = value;
    		$$invalidate(0, edit);
    	}

    	function inputfield_value_binding(value) {
    		edit.name = value;
    		$$invalidate(0, edit);
    	}

    	function arrayfield_value_binding(value, attribute) {
    		edit.data[attribute.name] = value;
    		$$invalidate(0, edit);
    	}

    	function inputfield_value_binding_1(value, attribute) {
    		edit.data[attribute.name] = value;
    		$$invalidate(0, edit);
    	}

    	$$self.$$set = $$props => {
    		if ("params" in $$props) $$invalidate(6, params = $$props.params);
    	};

    	$$self.$capture_state = () => ({
    		onMount,
    		push,
    		pop,
    		toastFail,
    		RequestManager,
    		Edit,
    		Entity,
    		Schema,
    		FormTemplate,
    		InputField,
    		ArrayField,
    		SelectField,
    		toastOnCondition,
    		toastClear,
    		params,
    		manager,
    		schema,
    		edit,
    		error,
    		waiting,
    		submit,
    		cancel
    	});

    	$$self.$inject_state = $$props => {
    		if ("params" in $$props) $$invalidate(6, params = $$props.params);
    		if ("edit" in $$props) $$invalidate(0, edit = $$props.edit);
    		if ("error" in $$props) $$invalidate(1, error = $$props.error);
    		if ("waiting" in $$props) $$invalidate(2, waiting = $$props.waiting);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	return [
    		edit,
    		error,
    		waiting,
    		schema,
    		submit,
    		cancel,
    		params,
    		selectfield_value_binding,
    		inputfield_value_binding,
    		arrayfield_value_binding,
    		inputfield_value_binding_1
    	];
    }

    class NodeEdit extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$b, create_fragment$b, safe_not_equal, { params: 6 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "NodeEdit",
    			options,
    			id: create_fragment$b.name
    		});
    	}

    	get params() {
    		throw new Error("<NodeEdit>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set params(value) {
    		throw new Error("<NodeEdit>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/common/MultiSelect.svelte generated by Svelte v3.24.1 */
    const file$b = "src/common/MultiSelect.svelte";

    function get_each_context$6(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[7] = list[i];
    	return child_ctx;
    }

    // (30:4) {#each options as option}
    function create_each_block$6(ctx) {
    	let option;
    	let t_value = /*option*/ ctx[7] + "";
    	let t;
    	let option_value_value;

    	const block = {
    		c: function create() {
    			option = element("option");
    			t = text(t_value);
    			option.__value = option_value_value = /*option*/ ctx[7];
    			option.value = option.__value;
    			add_location(option, file$b, 30, 8, 780);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, option, anchor);
    			append_dev(option, t);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*options*/ 2 && t_value !== (t_value = /*option*/ ctx[7] + "")) set_data_dev(t, t_value);

    			if (dirty & /*options*/ 2 && option_value_value !== (option_value_value = /*option*/ ctx[7])) {
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
    		id: create_each_block$6.name,
    		type: "each",
    		source: "(30:4) {#each options as option}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$c(ctx) {
    	let select;
    	let option;
    	let t0;
    	let t1;
    	let mounted;
    	let dispose;
    	let each_value = /*options*/ ctx[1];
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block$6(get_each_context$6(ctx, each_value, i));
    	}

    	const block = {
    		c: function create() {
    			select = element("select");
    			option = element("option");
    			t0 = text("Select ");
    			t1 = text(/*display*/ ctx[0]);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			option.__value = "";
    			option.value = option.__value;
    			add_location(option, file$b, 28, 4, 699);
    			select.multiple = "multiple";
    			attr_dev(select, "class", "ui fluid search dropdown multiple");
    			add_location(select, file$b, 24, 0, 558);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, select, anchor);
    			append_dev(select, option);
    			append_dev(option, t0);
    			append_dev(option, t1);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(select, null);
    			}

    			/*select_binding*/ ctx[5](select);

    			if (!mounted) {
    				dispose = listen_dev(select, "change", /*onChange*/ ctx[3], false, false, false);
    				mounted = true;
    			}
    		},
    		p: function update(ctx, [dirty]) {
    			if (dirty & /*display*/ 1) set_data_dev(t1, /*display*/ ctx[0]);

    			if (dirty & /*options*/ 2) {
    				each_value = /*options*/ ctx[1];
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context$6(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block$6(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(select, null);
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
    			if (detaching) detach_dev(select);
    			destroy_each(each_blocks, detaching);
    			/*select_binding*/ ctx[5](null);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$c.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$c($$self, $$props, $$invalidate) {
    	const dispatch = createEventDispatcher();
    	let { display } = $$props;
    	let { name } = $$props;
    	let { options = [] } = $$props;
    	let dropdown;

    	function onChange(event) {
    		const selectedValues = Array.from(event.target.selectedOptions).map(o => {
    			return o.value;
    		});

    		dispatch("update", { name, "value": selectedValues });
    	}

    	onMount(() => {
    		window.$(dropdown).dropdown();
    	});

    	const writable_props = ["display", "name", "options"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<MultiSelect> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("MultiSelect", $$slots, []);

    	function select_binding($$value) {
    		binding_callbacks[$$value ? "unshift" : "push"](() => {
    			dropdown = $$value;
    			$$invalidate(2, dropdown);
    			$$invalidate(1, options);
    		});
    	}

    	$$self.$$set = $$props => {
    		if ("display" in $$props) $$invalidate(0, display = $$props.display);
    		if ("name" in $$props) $$invalidate(4, name = $$props.name);
    		if ("options" in $$props) $$invalidate(1, options = $$props.options);
    	};

    	$$self.$capture_state = () => ({
    		onMount,
    		createEventDispatcher,
    		dispatch,
    		display,
    		name,
    		options,
    		dropdown,
    		onChange
    	});

    	$$self.$inject_state = $$props => {
    		if ("display" in $$props) $$invalidate(0, display = $$props.display);
    		if ("name" in $$props) $$invalidate(4, name = $$props.name);
    		if ("options" in $$props) $$invalidate(1, options = $$props.options);
    		if ("dropdown" in $$props) $$invalidate(2, dropdown = $$props.dropdown);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	return [display, options, dropdown, onChange, name, select_binding];
    }

    class MultiSelect extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$c, create_fragment$c, safe_not_equal, { display: 0, name: 4, options: 1 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "MultiSelect",
    			options,
    			id: create_fragment$c.name
    		});

    		const { ctx } = this.$$;
    		const props = options.props || {};

    		if (/*display*/ ctx[0] === undefined && !("display" in props)) {
    			console.warn("<MultiSelect> was created without expected prop 'display'");
    		}

    		if (/*name*/ ctx[4] === undefined && !("name" in props)) {
    			console.warn("<MultiSelect> was created without expected prop 'name'");
    		}
    	}

    	get display() {
    		throw new Error("<MultiSelect>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set display(value) {
    		throw new Error("<MultiSelect>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get name() {
    		throw new Error("<MultiSelect>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set name(value) {
    		throw new Error("<MultiSelect>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get options() {
    		throw new Error("<MultiSelect>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set options(value) {
    		throw new Error("<MultiSelect>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/views/ParseView.svelte generated by Svelte v3.24.1 */
    const file$c = "src/views/ParseView.svelte";

    function get_each_context_1$1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[10] = list[i];
    	return child_ctx;
    }

    function get_each_context$7(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[7] = list[i];
    	return child_ctx;
    }

    // (71:16) {:else}
    function create_else_block$7(ctx) {
    	let each_1_anchor;
    	let each_value = /*doc*/ ctx[0].spans;
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block$7(get_each_context$7(ctx, each_value, i));
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
    			if (dirty & /*openRow, doc*/ 33) {
    				each_value = /*doc*/ ctx[0].spans;
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context$7(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block$7(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(each_1_anchor.parentNode, each_1_anchor);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value.length;
    			}
    		},
    		d: function destroy(detaching) {
    			destroy_each(each_blocks, detaching);
    			if (detaching) detach_dev(each_1_anchor);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block$7.name,
    		type: "else",
    		source: "(71:16) {:else}",
    		ctx
    	});

    	return block;
    }

    // (69:16) {#if doc === null}
    function create_if_block$9(ctx) {
    	let tr;
    	let td;

    	const block = {
    		c: function create() {
    			tr = element("tr");
    			td = element("td");
    			td.textContent = "Failed to Parse.";
    			attr_dev(td, "colspan", "4");
    			add_location(td, file$c, 69, 24, 2136);
    			add_location(tr, file$c, 69, 20, 2132);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, tr, anchor);
    			append_dev(tr, td);
    		},
    		p: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(tr);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$9.name,
    		type: "if",
    		source: "(69:16) {#if doc === null}",
    		ctx
    	});

    	return block;
    }

    // (79:36) {#each span.tokens as token}
    function create_each_block_1$1(ctx) {
    	let tr;
    	let td0;
    	let t0_value = /*token*/ ctx[10].offset + "";
    	let t0;
    	let t1;
    	let td1;
    	let t2_value = /*token*/ ctx[10].token + "";
    	let t2;
    	let t3;

    	const block = {
    		c: function create() {
    			tr = element("tr");
    			td0 = element("td");
    			t0 = text(t0_value);
    			t1 = space();
    			td1 = element("td");
    			t2 = text(t2_value);
    			t3 = space();
    			attr_dev(td0, "class", "token_offset four wide");
    			add_location(td0, file$c, 80, 44, 2749);
    			attr_dev(td1, "class", "twelve wide");
    			add_location(td1, file$c, 81, 44, 2848);
    			add_location(tr, file$c, 79, 40, 2700);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, tr, anchor);
    			append_dev(tr, td0);
    			append_dev(td0, t0);
    			append_dev(tr, t1);
    			append_dev(tr, td1);
    			append_dev(td1, t2);
    			append_dev(tr, t3);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*doc*/ 1 && t0_value !== (t0_value = /*token*/ ctx[10].offset + "")) set_data_dev(t0, t0_value);
    			if (dirty & /*doc*/ 1 && t2_value !== (t2_value = /*token*/ ctx[10].token + "")) set_data_dev(t2, t2_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(tr);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block_1$1.name,
    		type: "each",
    		source: "(79:36) {#each span.tokens as token}",
    		ctx
    	});

    	return block;
    }

    // (72:20) {#each doc.spans as span}
    function create_each_block$7(ctx) {
    	let tr;
    	let td0;
    	let t0_value = /*span*/ ctx[7].entity.name + "";
    	let t0;
    	let t1;
    	let td1;
    	let t2_value = /*span*/ ctx[7].entity.label + "";
    	let t2;
    	let t3;
    	let td2;
    	let t4_value = /*span*/ ctx[7].entity.key + "";
    	let t4;
    	let t5;
    	let td3;
    	let table;
    	let t6;
    	let mounted;
    	let dispose;
    	let each_value_1 = /*span*/ ctx[7].tokens;
    	validate_each_argument(each_value_1);
    	let each_blocks = [];

    	for (let i = 0; i < each_value_1.length; i += 1) {
    		each_blocks[i] = create_each_block_1$1(get_each_context_1$1(ctx, each_value_1, i));
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
    			add_location(td0, file$c, 73, 28, 2338);
    			add_location(td1, file$c, 74, 28, 2394);
    			add_location(td2, file$c, 75, 28, 2451);
    			attr_dev(table, "class", "ui compact celled table top aligned");
    			add_location(table, file$c, 77, 32, 2543);
    			add_location(td3, file$c, 76, 28, 2506);
    			add_location(tr, file$c, 72, 24, 2273);
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
    						if (is_function(/*openRow*/ ctx[5](/*span*/ ctx[7].entity))) /*openRow*/ ctx[5](/*span*/ ctx[7].entity).apply(this, arguments);
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
    			if (dirty & /*doc*/ 1 && t0_value !== (t0_value = /*span*/ ctx[7].entity.name + "")) set_data_dev(t0, t0_value);
    			if (dirty & /*doc*/ 1 && t2_value !== (t2_value = /*span*/ ctx[7].entity.label + "")) set_data_dev(t2, t2_value);
    			if (dirty & /*doc*/ 1 && t4_value !== (t4_value = /*span*/ ctx[7].entity.key + "")) set_data_dev(t4, t4_value);

    			if (dirty & /*doc*/ 1) {
    				each_value_1 = /*span*/ ctx[7].tokens;
    				validate_each_argument(each_value_1);
    				let i;

    				for (i = 0; i < each_value_1.length; i += 1) {
    					const child_ctx = get_each_context_1$1(ctx, each_value_1, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block_1$1(child_ctx);
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
    		id: create_each_block$7.name,
    		type: "each",
    		source: "(72:20) {#each doc.spans as span}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$d(ctx) {
    	let div7;
    	let div4;
    	let h20;
    	let t1;
    	let div3;
    	let div0;
    	let label0;
    	let t3;
    	let textarea;
    	let t4;
    	let div1;
    	let label1;
    	let t6;
    	let multiselect;
    	let t7;
    	let div2;
    	let button;
    	let t9;
    	let div6;
    	let h21;
    	let t11;
    	let div5;
    	let table;
    	let thead;
    	let tr;
    	let th0;
    	let t13;
    	let th1;
    	let t15;
    	let th2;
    	let t17;
    	let th3;
    	let t19;
    	let tbody;
    	let current;
    	let mounted;
    	let dispose;

    	multiselect = new MultiSelect({
    			props: {
    				display: "Labels",
    				name: "labels",
    				options: /*schema*/ ctx[2].labels
    			},
    			$$inline: true
    		});

    	multiselect.$on("update", /*onUpdate*/ ctx[3]);

    	function select_block_type(ctx, dirty) {
    		if (/*doc*/ ctx[0] === null) return create_if_block$9;
    		return create_else_block$7;
    	}

    	let current_block_type = select_block_type(ctx);
    	let if_block = current_block_type(ctx);

    	const block = {
    		c: function create() {
    			div7 = element("div");
    			div4 = element("div");
    			h20 = element("h2");
    			h20.textContent = "Parse";
    			t1 = space();
    			div3 = element("div");
    			div0 = element("div");
    			label0 = element("label");
    			label0.textContent = "Text:";
    			t3 = space();
    			textarea = element("textarea");
    			t4 = space();
    			div1 = element("div");
    			label1 = element("label");
    			label1.textContent = "Labels:";
    			t6 = space();
    			create_component(multiselect.$$.fragment);
    			t7 = space();
    			div2 = element("div");
    			button = element("button");
    			button.textContent = "Parse";
    			t9 = space();
    			div6 = element("div");
    			h21 = element("h2");
    			h21.textContent = "Entities";
    			t11 = space();
    			div5 = element("div");
    			table = element("table");
    			thead = element("thead");
    			tr = element("tr");
    			th0 = element("th");
    			th0.textContent = "Name";
    			t13 = space();
    			th1 = element("th");
    			th1.textContent = "Label";
    			t15 = space();
    			th2 = element("th");
    			th2.textContent = "Key";
    			t17 = space();
    			th3 = element("th");
    			th3.textContent = "Tokens";
    			t19 = space();
    			tbody = element("tbody");
    			if_block.c();
    			add_location(h20, file$c, 32, 8, 809);
    			add_location(label0, file$c, 35, 16, 915);
    			attr_dev(textarea, "rows", "15");
    			add_location(textarea, file$c, 36, 16, 952);
    			attr_dev(div0, "class", "field");
    			add_location(div0, file$c, 34, 12, 879);
    			add_location(label1, file$c, 39, 16, 1081);
    			attr_dev(div1, "class", "field");
    			add_location(div1, file$c, 38, 12, 1045);
    			attr_dev(button, "class", "positive ui button");
    			add_location(button, file$c, 48, 16, 1391);
    			attr_dev(div2, "class", "field");
    			add_location(div2, file$c, 47, 12, 1355);
    			attr_dev(div3, "class", "ui form horizontally");
    			add_location(div3, file$c, 33, 8, 832);
    			attr_dev(div4, "class", "six wide column");
    			add_location(div4, file$c, 31, 4, 771);
    			add_location(h21, file$c, 55, 8, 1585);
    			attr_dev(th0, "class", "four wide");
    			add_location(th0, file$c, 61, 20, 1816);
    			attr_dev(th1, "class", "four wide");
    			add_location(th1, file$c, 62, 20, 1868);
    			attr_dev(th2, "class", "four wide");
    			add_location(th2, file$c, 63, 20, 1921);
    			attr_dev(th3, "class", "four wide");
    			add_location(th3, file$c, 64, 20, 1972);
    			add_location(tr, file$c, 60, 16, 1791);
    			attr_dev(thead, "class", "full-width");
    			add_location(thead, file$c, 59, 16, 1748);
    			add_location(tbody, file$c, 67, 16, 2069);
    			attr_dev(table, "class", "ui compact selectable celled striped table top aligned");
    			add_location(table, file$c, 58, 12, 1661);
    			attr_dev(div5, "class", "ui horizontally padded");
    			add_location(div5, file$c, 57, 8, 1612);
    			attr_dev(div6, "class", "ten wide column");
    			add_location(div6, file$c, 54, 4, 1547);
    			attr_dev(div7, "class", "ui stackable sixteen column grid");
    			add_location(div7, file$c, 30, 0, 720);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div7, anchor);
    			append_dev(div7, div4);
    			append_dev(div4, h20);
    			append_dev(div4, t1);
    			append_dev(div4, div3);
    			append_dev(div3, div0);
    			append_dev(div0, label0);
    			append_dev(div0, t3);
    			append_dev(div0, textarea);
    			set_input_value(textarea, /*nextRequest*/ ctx[1].text);
    			append_dev(div3, t4);
    			append_dev(div3, div1);
    			append_dev(div1, label1);
    			append_dev(div1, t6);
    			mount_component(multiselect, div1, null);
    			append_dev(div3, t7);
    			append_dev(div3, div2);
    			append_dev(div2, button);
    			append_dev(div7, t9);
    			append_dev(div7, div6);
    			append_dev(div6, h21);
    			append_dev(div6, t11);
    			append_dev(div6, div5);
    			append_dev(div5, table);
    			append_dev(table, thead);
    			append_dev(thead, tr);
    			append_dev(tr, th0);
    			append_dev(tr, t13);
    			append_dev(tr, th1);
    			append_dev(tr, t15);
    			append_dev(tr, th2);
    			append_dev(tr, t17);
    			append_dev(tr, th3);
    			append_dev(table, t19);
    			append_dev(table, tbody);
    			if_block.m(tbody, null);
    			current = true;

    			if (!mounted) {
    				dispose = [
    					listen_dev(textarea, "input", /*textarea_input_handler*/ ctx[6]),
    					listen_dev(button, "click", /*doParse*/ ctx[4], false, false, false)
    				];

    				mounted = true;
    			}
    		},
    		p: function update(ctx, [dirty]) {
    			if (dirty & /*nextRequest*/ 2) {
    				set_input_value(textarea, /*nextRequest*/ ctx[1].text);
    			}

    			if (current_block_type === (current_block_type = select_block_type(ctx)) && if_block) {
    				if_block.p(ctx, dirty);
    			} else {
    				if_block.d(1);
    				if_block = current_block_type(ctx);

    				if (if_block) {
    					if_block.c();
    					if_block.m(tbody, null);
    				}
    			}
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(multiselect.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(multiselect.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div7);
    			destroy_component(multiselect);
    			if_block.d();
    			mounted = false;
    			run_all(dispose);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$d.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$d($$self, $$props, $$invalidate) {
    	let schema = Schema.instance();
    	let doc = { text: "", spans: [], tokens: [] };
    	const nextRequest = { text: "", labels: [] };

    	const onUpdate = async event => {
    		$$invalidate(1, nextRequest[event.detail.name] = event.detail.value, nextRequest);
    	};

    	const doParse = async () => {
    		$$invalidate(0, doc = await manager.parseDoc(nextRequest));
    	};

    	const openRow = entity => {
    		push("/detail/" + entity.key);
    	};

    	document.title = "Parse Text";
    	const writable_props = [];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<ParseView> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("ParseView", $$slots, []);

    	function textarea_input_handler() {
    		nextRequest.text = this.value;
    		$$invalidate(1, nextRequest);
    	}

    	$$self.$capture_state = () => ({
    		onMount,
    		push,
    		MultiSelect,
    		manager,
    		Schema,
    		schema,
    		doc,
    		nextRequest,
    		onUpdate,
    		doParse,
    		openRow
    	});

    	$$self.$inject_state = $$props => {
    		if ("schema" in $$props) $$invalidate(2, schema = $$props.schema);
    		if ("doc" in $$props) $$invalidate(0, doc = $$props.doc);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	return [doc, nextRequest, schema, onUpdate, doParse, openRow, textarea_input_handler];
    }

    class ParseView extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$d, create_fragment$d, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "ParseView",
    			options,
    			id: create_fragment$d.name
    		});
    	}
    }

    /* src/common/SearchBox.svelte generated by Svelte v3.24.1 */
    const file$d = "src/common/SearchBox.svelte";

    // (35:4) {:else}
    function create_else_block$8(ctx) {
    	let button;
    	let i;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			button = element("button");
    			i = element("i");
    			attr_dev(i, "class", "search icon");
    			add_location(i, file$d, 36, 12, 854);
    			attr_dev(button, "class", "ui grey right icon button");
    			add_location(button, file$d, 35, 8, 781);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, button, anchor);
    			append_dev(button, i);

    			if (!mounted) {
    				dispose = listen_dev(button, "click", /*clearQ*/ ctx[2], false, false, false);
    				mounted = true;
    			}
    		},
    		p: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(button);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block$8.name,
    		type: "else",
    		source: "(35:4) {:else}",
    		ctx
    	});

    	return block;
    }

    // (31:4) {#if q}
    function create_if_block$a(ctx) {
    	let button;
    	let i;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			button = element("button");
    			i = element("i");
    			attr_dev(i, "class", "window close icon");
    			add_location(i, file$d, 32, 12, 709);
    			attr_dev(button, "class", "ui red right icon button");
    			add_location(button, file$d, 31, 8, 637);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, button, anchor);
    			append_dev(button, i);

    			if (!mounted) {
    				dispose = listen_dev(button, "click", /*clearQ*/ ctx[2], false, false, false);
    				mounted = true;
    			}
    		},
    		p: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(button);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$a.name,
    		type: "if",
    		source: "(31:4) {#if q}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$e(ctx) {
    	let div;
    	let input;
    	let t;
    	let mounted;
    	let dispose;

    	function select_block_type(ctx, dirty) {
    		if (/*q*/ ctx[0]) return create_if_block$a;
    		return create_else_block$8;
    	}

    	let current_block_type = select_block_type(ctx);
    	let if_block = current_block_type(ctx);

    	const block = {
    		c: function create() {
    			div = element("div");
    			input = element("input");
    			t = space();
    			if_block.c();
    			attr_dev(input, "size", "20");
    			attr_dev(input, "id", "search");
    			attr_dev(input, "type", "text");
    			attr_dev(input, "placeholder", "Search");
    			add_location(input, file$d, 26, 4, 497);
    			attr_dev(div, "id", "action-item");
    			attr_dev(div, "class", "ui fluid action input");
    			add_location(div, file$d, 25, 0, 440);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			append_dev(div, input);
    			/*input_binding*/ ctx[4](input);
    			set_input_value(input, /*q*/ ctx[0]);
    			append_dev(div, t);
    			if_block.m(div, null);

    			if (!mounted) {
    				dispose = listen_dev(input, "input", /*input_input_handler*/ ctx[5]);
    				mounted = true;
    			}
    		},
    		p: function update(ctx, [dirty]) {
    			if (dirty & /*q*/ 1 && input.value !== /*q*/ ctx[0]) {
    				set_input_value(input, /*q*/ ctx[0]);
    			}

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
    			/*input_binding*/ ctx[4](null);
    			if_block.d();
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$e.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$e($$self, $$props, $$invalidate) {
    	const dispatch = createEventDispatcher();
    	let { name } = $$props;
    	let { q = "" } = $$props;
    	let lastQ = q;
    	let qInput;

    	function clearQ() {
    		$$invalidate(0, q = "");
    		qInput.focus();
    	}

    	function updateQ() {
    		if (q !== lastQ) {
    			dispatch("update", { name, "value": q });
    			lastQ = q;
    		}
    	}

    	const writable_props = ["name", "q"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<SearchBox> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("SearchBox", $$slots, []);

    	function input_binding($$value) {
    		binding_callbacks[$$value ? "unshift" : "push"](() => {
    			qInput = $$value;
    			$$invalidate(1, qInput);
    		});
    	}

    	function input_input_handler() {
    		q = this.value;
    		$$invalidate(0, q);
    	}

    	$$self.$$set = $$props => {
    		if ("name" in $$props) $$invalidate(3, name = $$props.name);
    		if ("q" in $$props) $$invalidate(0, q = $$props.q);
    	};

    	$$self.$capture_state = () => ({
    		createEventDispatcher,
    		dispatch,
    		name,
    		q,
    		lastQ,
    		qInput,
    		clearQ,
    		updateQ
    	});

    	$$self.$inject_state = $$props => {
    		if ("name" in $$props) $$invalidate(3, name = $$props.name);
    		if ("q" in $$props) $$invalidate(0, q = $$props.q);
    		if ("lastQ" in $$props) lastQ = $$props.lastQ;
    		if ("qInput" in $$props) $$invalidate(1, qInput = $$props.qInput);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*q*/ 1) {
    			 updateQ();
    		}
    	};

    	return [q, qInput, clearQ, name, input_binding, input_input_handler];
    }

    class SearchBox extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$e, create_fragment$e, safe_not_equal, { name: 3, q: 0 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "SearchBox",
    			options,
    			id: create_fragment$e.name
    		});

    		const { ctx } = this.$$;
    		const props = options.props || {};

    		if (/*name*/ ctx[3] === undefined && !("name" in props)) {
    			console.warn("<SearchBox> was created without expected prop 'name'");
    		}
    	}

    	get name() {
    		throw new Error("<SearchBox>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set name(value) {
    		throw new Error("<SearchBox>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get q() {
    		throw new Error("<SearchBox>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set q(value) {
    		throw new Error("<SearchBox>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/views/NodeListing.svelte generated by Svelte v3.24.1 */
    const file$e = "src/views/NodeListing.svelte";

    function get_each_context_2$1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[16] = list[i];
    	return child_ctx;
    }

    function get_each_context_1$2(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[12] = list[i][0];
    	child_ctx[13] = list[i][1];
    	return child_ctx;
    }

    function get_each_context$8(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[9] = list[i];
    	return child_ctx;
    }

    // (85:4) {#if entities.length === 0}
    function create_if_block_2$3(ctx) {
    	let tr;
    	let td;

    	const block = {
    		c: function create() {
    			tr = element("tr");
    			td = element("td");
    			td.textContent = "No records found.";
    			attr_dev(td, "colspan", "4");
    			attr_dev(td, "class", "ui center aligned");
    			add_location(td, file$e, 86, 12, 2317);
    			add_location(tr, file$e, 85, 8, 2300);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, tr, anchor);
    			append_dev(tr, td);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(tr);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_2$3.name,
    		type: "if",
    		source: "(85:4) {#if entities.length === 0}",
    		ctx
    	});

    	return block;
    }

    // (110:32) {:else}
    function create_else_block$9(ctx) {
    	let t_value = /*value*/ ctx[13] + "";
    	let t;

    	const block = {
    		c: function create() {
    			t = text(t_value);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, t, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*entities*/ 2 && t_value !== (t_value = /*value*/ ctx[13] + "")) set_data_dev(t, t_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(t);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block$9.name,
    		type: "else",
    		source: "(110:32) {:else}",
    		ctx
    	});

    	return block;
    }

    // (103:32) {#if value instanceof Array}
    function create_if_block$b(ctx) {
    	let t;
    	let if_block_anchor;
    	let each_value_2 = /*value*/ ctx[13].slice(0, 5);
    	validate_each_argument(each_value_2);
    	let each_blocks = [];

    	for (let i = 0; i < each_value_2.length; i += 1) {
    		each_blocks[i] = create_each_block_2$1(get_each_context_2$1(ctx, each_value_2, i));
    	}

    	let if_block = /*value*/ ctx[13].length > 5 && create_if_block_1$6(ctx);

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
    			if (dirty & /*entities*/ 2) {
    				each_value_2 = /*value*/ ctx[13].slice(0, 5);
    				validate_each_argument(each_value_2);
    				let i;

    				for (i = 0; i < each_value_2.length; i += 1) {
    					const child_ctx = get_each_context_2$1(ctx, each_value_2, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block_2$1(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(t.parentNode, t);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value_2.length;
    			}

    			if (/*value*/ ctx[13].length > 5) {
    				if (if_block) {
    					if_block.p(ctx, dirty);
    				} else {
    					if_block = create_if_block_1$6(ctx);
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
    		id: create_if_block$b.name,
    		type: "if",
    		source: "(103:32) {#if value instanceof Array}",
    		ctx
    	});

    	return block;
    }

    // (104:36) {#each value.slice(0, 5) as item}
    function create_each_block_2$1(ctx) {
    	let t_value = /*item*/ ctx[16] + "";
    	let t;
    	let br;

    	const block = {
    		c: function create() {
    			t = text(t_value);
    			br = element("br");
    			add_location(br, file$e, 104, 46, 3117);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, t, anchor);
    			insert_dev(target, br, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*entities*/ 2 && t_value !== (t_value = /*item*/ ctx[16] + "")) set_data_dev(t, t_value);
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
    		source: "(104:36) {#each value.slice(0, 5) as item}",
    		ctx
    	});

    	return block;
    }

    // (107:36) {#if value.length > 5}
    function create_if_block_1$6(ctx) {
    	let i;
    	let t0_value = /*value*/ ctx[13].length - 5 + "";
    	let t0;
    	let t1;

    	const block = {
    		c: function create() {
    			i = element("i");
    			t0 = text(t0_value);
    			t1 = text(" more...");
    			add_location(i, file$e, 107, 40, 3266);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, i, anchor);
    			append_dev(i, t0);
    			append_dev(i, t1);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*entities*/ 2 && t0_value !== (t0_value = /*value*/ ctx[13].length - 5 + "")) set_data_dev(t0, t0_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(i);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_1$6.name,
    		type: "if",
    		source: "(107:36) {#if value.length > 5}",
    		ctx
    	});

    	return block;
    }

    // (99:20) {#each entity.attributes as [name, value]}
    function create_each_block_1$2(ctx) {
    	let tr;
    	let td0;
    	let t0_value = /*name*/ ctx[12] + "";
    	let t0;
    	let t1;
    	let t2;
    	let td1;
    	let t3;

    	function select_block_type(ctx, dirty) {
    		if (/*value*/ ctx[13] instanceof Array) return create_if_block$b;
    		return create_else_block$9;
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
    			add_location(td0, file$e, 100, 28, 2841);
    			attr_dev(td1, "class", "twelve wide");
    			add_location(td1, file$e, 101, 28, 2915);
    			attr_dev(tr, "class", "top aligned");
    			add_location(tr, file$e, 99, 24, 2788);
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
    			if (dirty & /*entities*/ 2 && t0_value !== (t0_value = /*name*/ ctx[12] + "")) set_data_dev(t0, t0_value);

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
    		id: create_each_block_1$2.name,
    		type: "each",
    		source: "(99:20) {#each entity.attributes as [name, value]}",
    		ctx
    	});

    	return block;
    }

    // (92:4) {#each entities as entity}
    function create_each_block$8(ctx) {
    	let tr;
    	let td0;
    	let t0_value = /*entity*/ ctx[9].name + "";
    	let t0;
    	let t1;
    	let td1;
    	let t2_value = /*entity*/ ctx[9].label + "";
    	let t2;
    	let t3;
    	let td2;
    	let t4_value = /*entity*/ ctx[9].key + "";
    	let t4;
    	let t5;
    	let td3;
    	let table;
    	let t6;
    	let mounted;
    	let dispose;
    	let each_value_1 = /*entity*/ ctx[9].attributes;
    	validate_each_argument(each_value_1);
    	let each_blocks = [];

    	for (let i = 0; i < each_value_1.length; i += 1) {
    		each_blocks[i] = create_each_block_1$2(get_each_context_1$2(ctx, each_value_1, i));
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
    			add_location(td0, file$e, 93, 12, 2523);
    			add_location(td1, file$e, 94, 12, 2558);
    			add_location(td2, file$e, 95, 12, 2594);
    			attr_dev(table, "class", "ui compact celled table top aligned");
    			add_location(table, file$e, 97, 16, 2649);
    			add_location(td3, file$e, 96, 12, 2628);
    			add_location(tr, file$e, 92, 8, 2475);
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
    						if (is_function(/*openRow*/ ctx[6](/*entity*/ ctx[9].key))) /*openRow*/ ctx[6](/*entity*/ ctx[9].key).apply(this, arguments);
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
    			if (dirty & /*entities*/ 2 && t0_value !== (t0_value = /*entity*/ ctx[9].name + "")) set_data_dev(t0, t0_value);
    			if (dirty & /*entities*/ 2 && t2_value !== (t2_value = /*entity*/ ctx[9].label + "")) set_data_dev(t2, t2_value);
    			if (dirty & /*entities*/ 2 && t4_value !== (t4_value = /*entity*/ ctx[9].key + "")) set_data_dev(t4, t4_value);

    			if (dirty & /*entities, Array*/ 2) {
    				each_value_1 = /*entity*/ ctx[9].attributes;
    				validate_each_argument(each_value_1);
    				let i;

    				for (i = 0; i < each_value_1.length; i += 1) {
    					const child_ctx = get_each_context_1$2(ctx, each_value_1, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block_1$2(child_ctx);
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
    		id: create_each_block$8.name,
    		type: "each",
    		source: "(92:4) {#each entities as entity}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$f(ctx) {
    	let div4;
    	let div0;
    	let h2;
    	let t1;
    	let div1;
    	let searchbox;
    	let t2;
    	let div2;
    	let multiselect;
    	let t3;
    	let div3;
    	let pagination;
    	let t4;
    	let table;
    	let thead;
    	let tr;
    	let th0;
    	let t6;
    	let th1;
    	let t8;
    	let th2;
    	let t10;
    	let th3;
    	let t12;
    	let tbody;
    	let t13;
    	let current;
    	searchbox = new SearchBox({ props: { name: "q" }, $$inline: true });
    	searchbox.$on("update", /*onUpdate*/ ctx[4]);

    	multiselect = new MultiSelect({
    			props: {
    				display: "Labels",
    				name: "labels",
    				options: /*schema*/ ctx[3].labels
    			},
    			$$inline: true
    		});

    	multiselect.$on("update", /*onUpdate*/ ctx[4]);

    	pagination = new Pagination({
    			props: {
    				page: /*nextRequest*/ ctx[0].page,
    				page_count: /*entities*/ ctx[1].length,
    				total_count: /*total_count*/ ctx[2]
    			},
    			$$inline: true
    		});

    	pagination.$on("doPageChange", /*doPageChange*/ ctx[5]);
    	let if_block = /*entities*/ ctx[1].length === 0 && create_if_block_2$3(ctx);
    	let each_value = /*entities*/ ctx[1];
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block$8(get_each_context$8(ctx, each_value, i));
    	}

    	const block = {
    		c: function create() {
    			div4 = element("div");
    			div0 = element("div");
    			h2 = element("h2");
    			h2.textContent = "Graph";
    			t1 = space();
    			div1 = element("div");
    			create_component(searchbox.$$.fragment);
    			t2 = space();
    			div2 = element("div");
    			create_component(multiselect.$$.fragment);
    			t3 = space();
    			div3 = element("div");
    			create_component(pagination.$$.fragment);
    			t4 = space();
    			table = element("table");
    			thead = element("thead");
    			tr = element("tr");
    			th0 = element("th");
    			th0.textContent = "Name";
    			t6 = space();
    			th1 = element("th");
    			th1.textContent = "Label";
    			t8 = space();
    			th2 = element("th");
    			th2.textContent = "Key";
    			t10 = space();
    			th3 = element("th");
    			th3.textContent = "Attributes";
    			t12 = space();
    			tbody = element("tbody");
    			if (if_block) if_block.c();
    			t13 = space();

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			add_location(h2, file$e, 52, 8, 1355);
    			attr_dev(div0, "class", "two wide column");
    			add_location(div0, file$e, 51, 4, 1317);
    			attr_dev(div1, "class", "five wide column");
    			add_location(div1, file$e, 54, 4, 1385);
    			attr_dev(div2, "class", "five wide column");
    			add_location(div2, file$e, 57, 4, 1482);
    			attr_dev(div3, "class", "four wide column");
    			add_location(div3, file$e, 65, 4, 1700);
    			attr_dev(div4, "class", "ui stackable sixteen column grid");
    			add_location(div4, file$e, 50, 0, 1266);
    			attr_dev(th0, "class", "two wide");
    			add_location(th0, file$e, 77, 8, 2070);
    			attr_dev(th1, "class", "two wide");
    			add_location(th1, file$e, 78, 8, 2109);
    			attr_dev(th2, "class", "two wide");
    			add_location(th2, file$e, 79, 8, 2149);
    			attr_dev(th3, "class", "four wide");
    			add_location(th3, file$e, 80, 8, 2187);
    			add_location(tr, file$e, 76, 4, 2057);
    			attr_dev(thead, "class", "full-width");
    			add_location(thead, file$e, 75, 4, 2026);
    			add_location(tbody, file$e, 83, 4, 2252);
    			attr_dev(table, "class", "ui compact selectable celled striped table top aligned");
    			add_location(table, file$e, 74, 0, 1951);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div4, anchor);
    			append_dev(div4, div0);
    			append_dev(div0, h2);
    			append_dev(div4, t1);
    			append_dev(div4, div1);
    			mount_component(searchbox, div1, null);
    			append_dev(div4, t2);
    			append_dev(div4, div2);
    			mount_component(multiselect, div2, null);
    			append_dev(div4, t3);
    			append_dev(div4, div3);
    			mount_component(pagination, div3, null);
    			insert_dev(target, t4, anchor);
    			insert_dev(target, table, anchor);
    			append_dev(table, thead);
    			append_dev(thead, tr);
    			append_dev(tr, th0);
    			append_dev(tr, t6);
    			append_dev(tr, th1);
    			append_dev(tr, t8);
    			append_dev(tr, th2);
    			append_dev(tr, t10);
    			append_dev(tr, th3);
    			append_dev(table, t12);
    			append_dev(table, tbody);
    			if (if_block) if_block.m(tbody, null);
    			append_dev(tbody, t13);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(tbody, null);
    			}

    			current = true;
    		},
    		p: function update(ctx, [dirty]) {
    			const pagination_changes = {};
    			if (dirty & /*nextRequest*/ 1) pagination_changes.page = /*nextRequest*/ ctx[0].page;
    			if (dirty & /*entities*/ 2) pagination_changes.page_count = /*entities*/ ctx[1].length;
    			if (dirty & /*total_count*/ 4) pagination_changes.total_count = /*total_count*/ ctx[2];
    			pagination.$set(pagination_changes);

    			if (/*entities*/ ctx[1].length === 0) {
    				if (if_block) ; else {
    					if_block = create_if_block_2$3(ctx);
    					if_block.c();
    					if_block.m(tbody, t13);
    				}
    			} else if (if_block) {
    				if_block.d(1);
    				if_block = null;
    			}

    			if (dirty & /*openRow, entities, Array*/ 66) {
    				each_value = /*entities*/ ctx[1];
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context$8(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block$8(child_ctx);
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
    			transition_in(searchbox.$$.fragment, local);
    			transition_in(multiselect.$$.fragment, local);
    			transition_in(pagination.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(searchbox.$$.fragment, local);
    			transition_out(multiselect.$$.fragment, local);
    			transition_out(pagination.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div4);
    			destroy_component(searchbox);
    			destroy_component(multiselect);
    			destroy_component(pagination);
    			if (detaching) detach_dev(t4);
    			if (detaching) detach_dev(table);
    			if (if_block) if_block.d();
    			destroy_each(each_blocks, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$f.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$f($$self, $$props, $$invalidate) {
    	let { params } = $$props;
    	const nextRequest = { q: "", labels: "", page: 0 };
    	let entities = [];
    	let total_count = null;
    	let schema = Schema.instance();

    	onMount(() => {
    		refreshData();
    	});

    	const refreshData = async () => {
    		$$invalidate(1, entities = await manager.getEntities(nextRequest));
    		$$invalidate(2, total_count = await manager.getTotalCount(nextRequest));
    	};

    	const onUpdate = async event => {
    		$$invalidate(0, nextRequest[event.detail.name] = event.detail.value, nextRequest);
    		$$invalidate(0, nextRequest["page"] = 0, nextRequest);
    		await refreshData();
    	};

    	async function doPageChange(event) {
    		$$invalidate(0, nextRequest["page"] = event.detail, nextRequest);
    		await refreshData();
    	}

    	const openRow = key => {
    		const encodedKey = encodeURIComponent(key);
    		push("/detail/" + encodedKey);
    		$$invalidate(0, nextRequest["page"] = 0, nextRequest);
    	};

    	document.title = "Graph Search";
    	const writable_props = ["params"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<NodeListing> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("NodeListing", $$slots, []);

    	$$self.$$set = $$props => {
    		if ("params" in $$props) $$invalidate(7, params = $$props.params);
    	};

    	$$self.$capture_state = () => ({
    		onMount,
    		push,
    		MultiSelect,
    		Pagination,
    		SearchBox,
    		manager,
    		Schema,
    		params,
    		nextRequest,
    		entities,
    		total_count,
    		schema,
    		refreshData,
    		onUpdate,
    		doPageChange,
    		openRow
    	});

    	$$self.$inject_state = $$props => {
    		if ("params" in $$props) $$invalidate(7, params = $$props.params);
    		if ("entities" in $$props) $$invalidate(1, entities = $$props.entities);
    		if ("total_count" in $$props) $$invalidate(2, total_count = $$props.total_count);
    		if ("schema" in $$props) $$invalidate(3, schema = $$props.schema);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	return [
    		nextRequest,
    		entities,
    		total_count,
    		schema,
    		onUpdate,
    		doPageChange,
    		openRow,
    		params
    	];
    }

    class NodeListing extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$f, create_fragment$f, safe_not_equal, { params: 7 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "NodeListing",
    			options,
    			id: create_fragment$f.name
    		});

    		const { ctx } = this.$$;
    		const props = options.props || {};

    		if (/*params*/ ctx[7] === undefined && !("params" in props)) {
    			console.warn("<NodeListing> was created without expected prop 'params'");
    		}
    	}

    	get params() {
    		throw new Error("<NodeListing>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set params(value) {
    		throw new Error("<NodeListing>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    var routes = {
        // documentation
        '/api': wrap({
            component: DocFrame,
            props: {source: "/docs", title: "Swagger UI"}
        }),
        '/docs': wrap({
            component: DocFrame,
            props: {source: "https://www.entitykb.org/", title: "Documentation"}
        }),

        '/parse': ParseView,
        '/detail/:key': NodeDetail,

        '/edit/:key': NodeEdit,
        '/add/': NodeEdit,

        '*': NodeListing,
    };

    const myToken = writable(null);

    const initToken = async () => {
        let token = localStorage.getItem("Token");
        myToken.set(token);
    };

    myToken.subscribe(newToken => {
        if (newToken !== null) {
            localStorage.setItem("Token", newToken);
        }
    });

    const removeToken = () => {
        myToken.set(null);
        localStorage.removeItem("Token");
    };

    const baseURL$1 = window.location.origin + "/";

    const loginUser = async (username, password) => {
        const url = 'token';
        const body = `username=${username}&password=${encodeURIComponent(password)}`;
        const contentType = 'application/x-www-form-urlencoded';
        const accessToken = await doFetch(url, body, contentType);

        let success = false;
        if (accessToken) {
            myToken.set(accessToken);
            success = true;
        }

        return success;
    };

    const doFetch = async (url, body, contentType) => {
        return await fetch(baseURL$1 + url, {
            method: 'POST',
            mode: 'cors',
            cache: 'no-cache',
            credentials: 'include',
            headers: {
                'accept': 'application/json',
                'Content-Type': contentType,
            },
            redirect: 'follow',
            referrerPolicy: 'no-referrer',
            body: body,
        })
            .then(async response => {
                const data = await response.json();
                return data.access_token;
            })
            .catch(async response => {
                console.log(response);
                return null;
            });
    };

    /* src/auth/LoginForm.svelte generated by Svelte v3.24.1 */
    const file$f = "src/auth/LoginForm.svelte";

    // (46:4) {:else}
    function create_else_block$a(ctx) {
    	let div;

    	const block = {
    		c: function create() {
    			div = element("div");
    			div.textContent = " ";
    			add_location(div, file$f, 46, 8, 1267);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block$a.name,
    		type: "else",
    		source: "(46:4) {:else}",
    		ctx
    	});

    	return block;
    }

    // (42:4) {#if hasError }
    function create_if_block$c(ctx) {
    	let div;

    	const block = {
    		c: function create() {
    			div = element("div");
    			div.textContent = "Invalid Username or Password";
    			attr_dev(div, "class", "ui visible error message");
    			add_location(div, file$f, 42, 8, 1152);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$c.name,
    		type: "if",
    		source: "(42:4) {#if hasError }",
    		ctx
    	});

    	return block;
    }

    function create_fragment$g(ctx) {
    	let h2;
    	let t1;
    	let form;
    	let div1;
    	let div0;
    	let i0;
    	let t2;
    	let input0;
    	let t3;
    	let div3;
    	let div2;
    	let i1;
    	let t4;
    	let input1;
    	let t5;
    	let div4;
    	let button;
    	let t7;
    	let mounted;
    	let dispose;

    	function select_block_type(ctx, dirty) {
    		if (/*hasError*/ ctx[0]) return create_if_block$c;
    		return create_else_block$a;
    	}

    	let current_block_type = select_block_type(ctx);
    	let if_block = current_block_type(ctx);

    	const block = {
    		c: function create() {
    			h2 = element("h2");
    			h2.textContent = "Login";
    			t1 = space();
    			form = element("form");
    			div1 = element("div");
    			div0 = element("div");
    			i0 = element("i");
    			t2 = space();
    			input0 = element("input");
    			t3 = space();
    			div3 = element("div");
    			div2 = element("div");
    			i1 = element("i");
    			t4 = space();
    			input1 = element("input");
    			t5 = space();
    			div4 = element("div");
    			button = element("button");
    			button.textContent = "Submit";
    			t7 = space();
    			if_block.c();
    			attr_dev(h2, "class", "svelte-174srti");
    			add_location(h2, file$f, 17, 0, 416);
    			attr_dev(i0, "class", "user icon");
    			add_location(i0, file$f, 22, 12, 574);
    			input0.required = "required";
    			attr_dev(input0, "type", "text");
    			attr_dev(input0, "name", "username");
    			attr_dev(input0, "placeholder", "Username");
    			add_location(input0, file$f, 23, 12, 612);
    			attr_dev(div0, "class", "ui left icon input");
    			add_location(div0, file$f, 21, 8, 529);
    			attr_dev(div1, "class", "field");
    			add_location(div1, file$f, 20, 4, 501);
    			attr_dev(i1, "class", "lock icon");
    			add_location(i1, file$f, 29, 12, 813);
    			input1.required = "required";
    			attr_dev(input1, "type", "password");
    			attr_dev(input1, "name", "password");
    			attr_dev(input1, "placeholder", "Password");
    			add_location(input1, file$f, 30, 12, 851);
    			attr_dev(div2, "class", "ui left icon input");
    			add_location(div2, file$f, 28, 8, 768);
    			attr_dev(div3, "class", "field");
    			add_location(div3, file$f, 27, 4, 740);
    			attr_dev(button, "class", "ui large primary submit button");
    			attr_dev(button, "type", "submit");
    			add_location(button, file$f, 36, 8, 998);
    			add_location(div4, file$f, 35, 4, 984);
    			attr_dev(form, "class", "ui large form");
    			add_location(form, file$f, 19, 0, 432);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, h2, anchor);
    			insert_dev(target, t1, anchor);
    			insert_dev(target, form, anchor);
    			append_dev(form, div1);
    			append_dev(div1, div0);
    			append_dev(div0, i0);
    			append_dev(div0, t2);
    			append_dev(div0, input0);
    			append_dev(form, t3);
    			append_dev(form, div3);
    			append_dev(div3, div2);
    			append_dev(div2, i1);
    			append_dev(div2, t4);
    			append_dev(div2, input1);
    			append_dev(form, t5);
    			append_dev(form, div4);
    			append_dev(div4, button);
    			append_dev(form, t7);
    			if_block.m(form, null);

    			if (!mounted) {
    				dispose = listen_dev(form, "submit", prevent_default(/*onSubmit*/ ctx[1]), false, true, false);
    				mounted = true;
    			}
    		},
    		p: function update(ctx, [dirty]) {
    			if (current_block_type !== (current_block_type = select_block_type(ctx))) {
    				if_block.d(1);
    				if_block = current_block_type(ctx);

    				if (if_block) {
    					if_block.c();
    					if_block.m(form, null);
    				}
    			}
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(h2);
    			if (detaching) detach_dev(t1);
    			if (detaching) detach_dev(form);
    			if_block.d();
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$g.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$g($$self, $$props, $$invalidate) {
    	const dispatch = createEventDispatcher();
    	let hasError = false;

    	const onSubmit = async e => {
    		const success = await loginUser(e.target.elements["username"].value, e.target.elements["password"].value);
    		$$invalidate(0, hasError = !success);
    	};

    	const writable_props = [];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<LoginForm> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("LoginForm", $$slots, []);

    	$$self.$capture_state = () => ({
    		createEventDispatcher,
    		loginUser,
    		dispatch,
    		hasError,
    		onSubmit
    	});

    	$$self.$inject_state = $$props => {
    		if ("hasError" in $$props) $$invalidate(0, hasError = $$props.hasError);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	return [hasError, onSubmit];
    }

    class LoginForm extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$g, create_fragment$g, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "LoginForm",
    			options,
    			id: create_fragment$g.name
    		});
    	}
    }

    /* src/auth/AuthMain.svelte generated by Svelte v3.24.1 */
    const file$g = "src/auth/AuthMain.svelte";

    function create_fragment$h(ctx) {
    	let div2;
    	let div1;
    	let h1;
    	let i;
    	let t0;
    	let t1;
    	let div0;
    	let loginform;
    	let current;
    	loginform = new LoginForm({ $$inline: true });

    	const block = {
    		c: function create() {
    			div2 = element("div");
    			div1 = element("div");
    			h1 = element("h1");
    			i = element("i");
    			t0 = text(" EntityKB");
    			t1 = space();
    			div0 = element("div");
    			create_component(loginform.$$.fragment);
    			attr_dev(i, "class", "lightbulb outline icon");
    			add_location(i, file$g, 7, 12, 213);
    			attr_dev(h1, "class", "ui image header svelte-1vnwc89");
    			add_location(h1, file$g, 6, 8, 172);
    			attr_dev(div0, "id", "authContent");
    			attr_dev(div0, "class", "ui top attached stacked segment svelte-1vnwc89");
    			add_location(div0, file$g, 9, 8, 283);
    			attr_dev(div1, "class", "column svelte-1vnwc89");
    			add_location(div1, file$g, 5, 4, 143);
    			attr_dev(div2, "id", "authContainer");
    			attr_dev(div2, "class", "ui middle aligned center aligned grid svelte-1vnwc89");
    			add_location(div2, file$g, 4, 0, 68);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div2, anchor);
    			append_dev(div2, div1);
    			append_dev(div1, h1);
    			append_dev(h1, i);
    			append_dev(h1, t0);
    			append_dev(div1, t1);
    			append_dev(div1, div0);
    			mount_component(loginform, div0, null);
    			current = true;
    		},
    		p: noop,
    		i: function intro(local) {
    			if (current) return;
    			transition_in(loginform.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(loginform.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div2);
    			destroy_component(loginform);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$h.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$h($$self, $$props, $$invalidate) {
    	const writable_props = [];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<AuthMain> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("AuthMain", $$slots, []);
    	$$self.$capture_state = () => ({ LoginForm });
    	return [];
    }

    class AuthMain extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$h, create_fragment$h, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "AuthMain",
    			options,
    			id: create_fragment$h.name
    		});
    	}
    }

    /* src/common/TopMenu.svelte generated by Svelte v3.24.1 */
    const file$h = "src/common/TopMenu.svelte";

    function create_fragment$i(ctx) {
    	let div;
    	let a0;
    	let i0;
    	let t0;
    	let link_action;
    	let t1;
    	let a1;
    	let i1;
    	let t2;
    	let link_action_1;
    	let t3;
    	let a2;
    	let i2;
    	let t4;
    	let link_action_2;
    	let t5;
    	let a3;
    	let i3;
    	let t6;
    	let link_action_3;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			div = element("div");
    			a0 = element("a");
    			i0 = element("i");
    			t0 = text(" Graph");
    			t1 = space();
    			a1 = element("a");
    			i1 = element("i");
    			t2 = text(" Parse");
    			t3 = space();
    			a2 = element("a");
    			i2 = element("i");
    			t4 = text(" API");
    			t5 = space();
    			a3 = element("a");
    			i3 = element("i");
    			t6 = text(" Docs");
    			attr_dev(i0, "class", "vector square icon");
    			add_location(i0, file$h, 12, 8, 300);
    			attr_dev(a0, "href", "/");
    			attr_dev(a0, "class", "item");
    			add_location(a0, file$h, 11, 4, 257);
    			attr_dev(i1, "class", "highlighter icon");
    			add_location(i1, file$h, 20, 8, 527);
    			attr_dev(a1, "href", "/parse");
    			attr_dev(a1, "class", "item");
    			add_location(a1, file$h, 19, 4, 479);
    			attr_dev(i2, "class", "bolt icon");
    			add_location(i2, file$h, 24, 8, 626);
    			attr_dev(a2, "href", "/api");
    			attr_dev(a2, "class", "item");
    			add_location(a2, file$h, 23, 4, 580);
    			attr_dev(i3, "class", "book open icon");
    			add_location(i3, file$h, 28, 8, 717);
    			attr_dev(a3, "href", "/docs");
    			attr_dev(a3, "class", "item");
    			add_location(a3, file$h, 27, 4, 670);
    			attr_dev(div, "class", "ui four item inverted menu");
    			add_location(div, file$h, 10, 0, 212);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			append_dev(div, a0);
    			append_dev(a0, i0);
    			append_dev(a0, t0);
    			append_dev(div, t1);
    			append_dev(div, a1);
    			append_dev(a1, i1);
    			append_dev(a1, t2);
    			append_dev(div, t3);
    			append_dev(div, a2);
    			append_dev(a2, i2);
    			append_dev(a2, t4);
    			append_dev(div, t5);
    			append_dev(div, a3);
    			append_dev(a3, i3);
    			append_dev(a3, t6);

    			if (!mounted) {
    				dispose = [
    					action_destroyer(link_action = link.call(null, a0)),
    					action_destroyer(link_action_1 = link.call(null, a1)),
    					action_destroyer(link_action_2 = link.call(null, a2)),
    					action_destroyer(link_action_3 = link.call(null, a3))
    				];

    				mounted = true;
    			}
    		},
    		p: noop,
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    			mounted = false;
    			run_all(dispose);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$i.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$i($$self, $$props, $$invalidate) {
    	const logout = async () => {
    		removeToken();
    		await replace("/");
    	};

    	const writable_props = [];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<TopMenu> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("TopMenu", $$slots, []);
    	$$self.$capture_state = () => ({ removeToken, replace, link, logout });
    	return [];
    }

    class TopMenu extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$i, create_fragment$i, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "TopMenu",
    			options,
    			id: create_fragment$i.name
    		});
    	}
    }

    /* src/common/BottomMenu.svelte generated by Svelte v3.24.1 */
    const file$i = "src/common/BottomMenu.svelte";

    function create_fragment$j(ctx) {
    	let div3;
    	let a0;
    	let i0;
    	let t0;
    	let a0_href_value;
    	let t1;
    	let div0;
    	let t2;
    	let div1;
    	let t3;
    	let div2;
    	let a1;
    	let i1;
    	let t4;
    	let a2;
    	let i2;
    	let t5;
    	let a3;
    	let i3;
    	let t6;
    	let a4;
    	let i4;
    	let t7;
    	let a5;
    	let i5;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			div3 = element("div");
    			a0 = element("a");
    			i0 = element("i");
    			t0 = text(" Logout");
    			t1 = space();
    			div0 = element("div");
    			t2 = space();
    			div1 = element("div");
    			t3 = space();
    			div2 = element("div");
    			a1 = element("a");
    			i1 = element("i");
    			t4 = space();
    			a2 = element("a");
    			i2 = element("i");
    			t5 = space();
    			a3 = element("a");
    			i3 = element("i");
    			t6 = space();
    			a4 = element("a");
    			i4 = element("i");
    			t7 = space();
    			a5 = element("a");
    			i5 = element("i");
    			attr_dev(i0, "class", "sign out alternative icon");
    			add_location(i0, file$i, 13, 8, 325);
    			attr_dev(a0, "href", a0_href_value = "#");
    			attr_dev(a0, "class", "item");
    			add_location(a0, file$i, 12, 4, 271);
    			attr_dev(div0, "class", "item");
    			add_location(div0, file$i, 20, 4, 506);
    			attr_dev(div1, "class", "item");
    			add_location(div1, file$i, 23, 4, 541);
    			attr_dev(i1, "class", "large lightbulb outline icon");
    			add_location(i1, file$i, 28, 12, 652);
    			attr_dev(a1, "href", "https://www.entitykb.org/");
    			add_location(a1, file$i, 27, 8, 603);
    			attr_dev(i2, "class", "large github icon");
    			add_location(i2, file$i, 31, 12, 783);
    			attr_dev(a2, "href", "https://github.com/genomoncology/entitykb");
    			add_location(a2, file$i, 30, 8, 718);
    			attr_dev(i3, "class", "large twitter icon");
    			add_location(i3, file$i, 34, 12, 895);
    			attr_dev(a3, "href", "https://twitter.com/genomoncology");
    			add_location(a3, file$i, 33, 8, 838);
    			attr_dev(i4, "class", "large linkedin icon");
    			add_location(i4, file$i, 37, 12, 1021);
    			attr_dev(a4, "href", "https://www.linkedin.com/company/genomoncology");
    			add_location(a4, file$i, 36, 8, 951);
    			attr_dev(i5, "class", "large globe icon");
    			add_location(i5, file$i, 40, 12, 1131);
    			attr_dev(a5, "href", "https://www.genomoncology.com");
    			add_location(a5, file$i, 39, 8, 1078);
    			attr_dev(div2, "class", "item");
    			add_location(div2, file$i, 26, 4, 576);
    			attr_dev(div3, "class", "ui four item bottom fixed inverted menu");
    			add_location(div3, file$i, 11, 0, 213);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div3, anchor);
    			append_dev(div3, a0);
    			append_dev(a0, i0);
    			append_dev(a0, t0);
    			append_dev(div3, t1);
    			append_dev(div3, div0);
    			append_dev(div3, t2);
    			append_dev(div3, div1);
    			append_dev(div3, t3);
    			append_dev(div3, div2);
    			append_dev(div2, a1);
    			append_dev(a1, i1);
    			append_dev(div2, t4);
    			append_dev(div2, a2);
    			append_dev(a2, i2);
    			append_dev(div2, t5);
    			append_dev(div2, a3);
    			append_dev(a3, i3);
    			append_dev(div2, t6);
    			append_dev(div2, a4);
    			append_dev(a4, i4);
    			append_dev(div2, t7);
    			append_dev(div2, a5);
    			append_dev(a5, i5);

    			if (!mounted) {
    				dispose = listen_dev(a0, "click", /*logout*/ ctx[0], false, false, false);
    				mounted = true;
    			}
    		},
    		p: noop,
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div3);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$j.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$j($$self, $$props, $$invalidate) {
    	const logout = async () => {
    		removeToken();
    		await replace("/");
    	};

    	const writable_props = [];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<BottomMenu> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("BottomMenu", $$slots, []);
    	$$self.$capture_state = () => ({ removeToken, replace, link, logout });
    	return [logout];
    }

    class BottomMenu extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$j, create_fragment$j, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "BottomMenu",
    			options,
    			id: create_fragment$j.name
    		});
    	}
    }

    /* src/App.svelte generated by Svelte v3.24.1 */
    const file$j = "src/App.svelte";

    // (45:0) {:else}
    function create_else_block$b(ctx) {
    	let authmain;
    	let current;
    	authmain = new AuthMain({ $$inline: true });

    	const block = {
    		c: function create() {
    			create_component(authmain.$$.fragment);
    		},
    		m: function mount(target, anchor) {
    			mount_component(authmain, target, anchor);
    			current = true;
    		},
    		p: noop,
    		i: function intro(local) {
    			if (current) return;
    			transition_in(authmain.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(authmain.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			destroy_component(authmain, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block$b.name,
    		type: "else",
    		source: "(45:0) {:else}",
    		ctx
    	});

    	return block;
    }

    // (37:0) {#if token}
    function create_if_block$d(ctx) {
    	let topmenu;
    	let t0;
    	let div;
    	let router;
    	let t1;
    	let bottommenu;
    	let current;
    	topmenu = new TopMenu({ $$inline: true });
    	router = new Router({ props: { routes }, $$inline: true });
    	bottommenu = new BottomMenu({ $$inline: true });

    	const block = {
    		c: function create() {
    			create_component(topmenu.$$.fragment);
    			t0 = space();
    			div = element("div");
    			create_component(router.$$.fragment);
    			t1 = space();
    			create_component(bottommenu.$$.fragment);
    			attr_dev(div, "id", "appContainer");
    			attr_dev(div, "class", "svelte-12xy2y4");
    			add_location(div, file$j, 39, 4, 893);
    		},
    		m: function mount(target, anchor) {
    			mount_component(topmenu, target, anchor);
    			insert_dev(target, t0, anchor);
    			insert_dev(target, div, anchor);
    			mount_component(router, div, null);
    			insert_dev(target, t1, anchor);
    			mount_component(bottommenu, target, anchor);
    			current = true;
    		},
    		p: noop,
    		i: function intro(local) {
    			if (current) return;
    			transition_in(topmenu.$$.fragment, local);
    			transition_in(router.$$.fragment, local);
    			transition_in(bottommenu.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(topmenu.$$.fragment, local);
    			transition_out(router.$$.fragment, local);
    			transition_out(bottommenu.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			destroy_component(topmenu, detaching);
    			if (detaching) detach_dev(t0);
    			if (detaching) detach_dev(div);
    			destroy_component(router);
    			if (detaching) detach_dev(t1);
    			destroy_component(bottommenu, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$d.name,
    		type: "if",
    		source: "(37:0) {#if token}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$k(ctx) {
    	let current_block_type_index;
    	let if_block;
    	let t;
    	let sveltetoast;
    	let current;
    	const if_block_creators = [create_if_block$d, create_else_block$b];
    	const if_blocks = [];

    	function select_block_type(ctx, dirty) {
    		if (/*token*/ ctx[0]) return 0;
    		return 1;
    	}

    	current_block_type_index = select_block_type(ctx);
    	if_block = if_blocks[current_block_type_index] = if_block_creators[current_block_type_index](ctx);

    	sveltetoast = new SvelteToast({
    			props: { options: /*options*/ ctx[1] },
    			$$inline: true
    		});

    	const block = {
    		c: function create() {
    			if_block.c();
    			t = space();
    			create_component(sveltetoast.$$.fragment);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			if_blocks[current_block_type_index].m(target, anchor);
    			insert_dev(target, t, anchor);
    			mount_component(sveltetoast, target, anchor);
    			current = true;
    		},
    		p: function update(ctx, [dirty]) {
    			let previous_block_index = current_block_type_index;
    			current_block_type_index = select_block_type(ctx);

    			if (current_block_type_index === previous_block_index) {
    				if_blocks[current_block_type_index].p(ctx, dirty);
    			} else {
    				group_outros();

    				transition_out(if_blocks[previous_block_index], 1, 1, () => {
    					if_blocks[previous_block_index] = null;
    				});

    				check_outros();
    				if_block = if_blocks[current_block_type_index];

    				if (!if_block) {
    					if_block = if_blocks[current_block_type_index] = if_block_creators[current_block_type_index](ctx);
    					if_block.c();
    				}

    				transition_in(if_block, 1);
    				if_block.m(t.parentNode, t);
    			}
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(if_block);
    			transition_in(sveltetoast.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(if_block);
    			transition_out(sveltetoast.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if_blocks[current_block_type_index].d(detaching);
    			if (detaching) detach_dev(t);
    			destroy_component(sveltetoast, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$k.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$k($$self, $$props, $$invalidate) {
    	onMount(async () => {
    		await Schema.instance().load();
    		await initToken();
    	});

    	let token = null;

    	myToken.subscribe(newToken => {
    		$$invalidate(0, token = newToken);
    	});

    	const options = {
    		theme: {
    			"--toastWidth": "20rem",
    			"--toastHeight": "5rem"
    		},
    		duration: 1500
    	};

    	const writable_props = [];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<App> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("App", $$slots, []);

    	$$self.$capture_state = () => ({
    		onMount,
    		SvelteToast,
    		Router,
    		routes,
    		AuthMain,
    		initToken,
    		myToken,
    		Schema,
    		TopMenu,
    		BottomMenu,
    		token,
    		options
    	});

    	$$self.$inject_state = $$props => {
    		if ("token" in $$props) $$invalidate(0, token = $$props.token);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	return [token, options];
    }

    class App extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$k, create_fragment$k, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "App",
    			options,
    			id: create_fragment$k.name
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
