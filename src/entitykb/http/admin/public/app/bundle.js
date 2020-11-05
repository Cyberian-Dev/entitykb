
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

    const baseURL = window.location.origin;
    const searchURL = baseURL + "/search";
    const pageSize = 10;

    const search = async (term, key, label, attr_name, attr_value, page) => {
        let traversal = [];

        if (key) {
            traversal.push({
                "criteria": [
                    {
                        "type": "field",
                        "field": "key",
                        "compare": "icontains",
                        "value": key,
                    }
                ]
            });
        }

        if (label) {
            traversal.push({
                "criteria": [
                    {
                        "type": "field",
                        "field": "label",
                        "compare": "icontains",
                        "value": label,
                    }
                ]
            });
        }

        if (attr_name && attr_value) {
            traversal.push({
                "criteria": [
                    {
                        "type": "field",
                        "field": attr_name,
                        "compare": "icontains",
                        "value": attr_value,
                    }
                ]
            });
        }

        const body = {
            'q': term,
            'limit': pageSize,
            'offset': page * pageSize,
            'traversal': traversal,
        };

        return await fetch(searchURL, {
            method: 'POST',
            mode: 'cors',
            cache: 'no-cache',
            credentials: 'same-origin',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json',
            },
            redirect: 'follow',
            referrerPolicy: 'no-referrer',
            body: JSON.stringify(body),
        })
            .then(response => {
                return response.json()
            })
            .catch(async response => {
                console.log(response);
                return {"nodes": [], "trails": []};
            });
    };

    /* src/Pagination.svelte generated by Svelte v3.24.1 */

    const file$2 = "src/Pagination.svelte";

    function get_each_context(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[5] = list[i];
    	return child_ctx;
    }

    // (40:8) {:else}
    function create_else_block(ctx) {
    	let a;
    	let t0_value = /*item*/ ctx[5] + 1 + "";
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
    			attr_dev(a, "data-value", a_data_value_value = /*item*/ ctx[5]);
    			toggle_class(a, "active", /*item*/ ctx[5] === /*page*/ ctx[0]);
    			add_location(a, file$2, 40, 8, 887);
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
    			if (dirty & /*items*/ 2 && t0_value !== (t0_value = /*item*/ ctx[5] + 1 + "")) set_data_dev(t0, t0_value);

    			if (dirty & /*items*/ 2 && a_data_value_value !== (a_data_value_value = /*item*/ ctx[5])) {
    				attr_dev(a, "data-value", a_data_value_value);
    			}

    			if (dirty & /*items, page*/ 3) {
    				toggle_class(a, "active", /*item*/ ctx[5] === /*page*/ ctx[0]);
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
    		source: "(40:8) {:else}",
    		ctx
    	});

    	return block;
    }

    // (38:8) {#if item === null}
    function create_if_block(ctx) {
    	let a;

    	const block = {
    		c: function create() {
    			a = element("a");
    			a.textContent = "...";
    			attr_dev(a, "class", "disabled item svelte-947s4u");
    			add_location(a, file$2, 38, 12, 830);
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
    		source: "(38:8) {#if item === null}",
    		ctx
    	});

    	return block;
    }

    // (37:4) {#each items as item}
    function create_each_block(ctx) {
    	let if_block_anchor;

    	function select_block_type(ctx, dirty) {
    		if (/*item*/ ctx[5] === null) return create_if_block;
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
    		source: "(37:4) {#each items as item}",
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

    			add_location(b, file$2, 33, 0, 712);
    			attr_dev(div, "class", "ui pagination tiny menu svelte-947s4u");
    			add_location(div, file$2, 35, 0, 726);
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

    /* src/Admin.svelte generated by Svelte v3.24.1 */

    const { Object: Object_1 } = globals;
    const file$3 = "src/Admin.svelte";

    function get_each_context_1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[22] = list[i];
    	return child_ctx;
    }

    function get_each_context_2(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[25] = list[i];
    	return child_ctx;
    }

    function get_each_context$1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[19] = list[i];
    	return child_ctx;
    }

    // (54:8) {:else}
    function create_else_block$1(ctx) {
    	let button;
    	let i;
    	let t;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			button = element("button");
    			i = element("i");
    			t = text("\n            Show Filters");
    			attr_dev(i, "class", "filter icon");
    			add_location(i, file$3, 55, 12, 1389);
    			attr_dev(button, "class", "ui labeled icon blue button");
    			add_location(button, file$3, 54, 8, 1309);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, button, anchor);
    			append_dev(button, i);
    			append_dev(button, t);

    			if (!mounted) {
    				dispose = listen_dev(button, "click", /*showFilters*/ ctx[9], false, false, false);
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
    		id: create_else_block$1.name,
    		type: "else",
    		source: "(54:8) {:else}",
    		ctx
    	});

    	return block;
    }

    // (49:8) {#if showFilter}
    function create_if_block_3(ctx) {
    	let button;
    	let i;
    	let t;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			button = element("button");
    			i = element("i");
    			t = text("\n          Clear Filters");
    			attr_dev(i, "class", "minus circle icon");
    			add_location(i, file$3, 50, 10, 1209);
    			attr_dev(button, "class", "ui labeled icon red button");
    			add_location(button, file$3, 49, 8, 1131);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, button, anchor);
    			append_dev(button, i);
    			append_dev(button, t);

    			if (!mounted) {
    				dispose = listen_dev(button, "click", /*clearFilters*/ ctx[10], false, false, false);
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
    		id: create_if_block_3.name,
    		type: "if",
    		source: "(49:8) {#if showFilter}",
    		ctx
    	});

    	return block;
    }

    // (82:4) {#if showFilter}
    function create_if_block_2(ctx) {
    	let tr;
    	let th0;
    	let input0;
    	let t0;
    	let th1;
    	let input1;
    	let t1;
    	let th2;
    	let input2;
    	let t2;
    	let th3;
    	let input3;
    	let t3;
    	let input4;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			tr = element("tr");
    			th0 = element("th");
    			input0 = element("input");
    			t0 = space();
    			th1 = element("th");
    			input1 = element("input");
    			t1 = space();
    			th2 = element("th");
    			input2 = element("input");
    			t2 = space();
    			th3 = element("th");
    			input3 = element("input");
    			t3 = text("\n            ≈\n            ");
    			input4 = element("input");
    			attr_dev(input0, "placeholder", "prefix");
    			add_location(input0, file$3, 83, 12, 2029);
    			add_location(th0, file$3, 83, 8, 2025);
    			attr_dev(input1, "placeholder", "key");
    			add_location(input1, file$3, 84, 12, 2093);
    			add_location(th1, file$3, 84, 8, 2089);
    			attr_dev(input2, "placeholder", "label");
    			add_location(input2, file$3, 85, 12, 2153);
    			add_location(th2, file$3, 85, 8, 2149);
    			attr_dev(input3, "placeholder", "name");
    			add_location(input3, file$3, 87, 12, 2246);
    			attr_dev(input4, "placeholder", "value");
    			add_location(input4, file$3, 89, 12, 2334);
    			attr_dev(th3, "nowrap", "nowrap");
    			add_location(th3, file$3, 86, 8, 2213);
    			attr_dev(tr, "class", "center aligned");
    			add_location(tr, file$3, 82, 4, 1989);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, tr, anchor);
    			append_dev(tr, th0);
    			append_dev(th0, input0);
    			set_input_value(input0, /*term*/ ctx[0]);
    			append_dev(tr, t0);
    			append_dev(tr, th1);
    			append_dev(th1, input1);
    			set_input_value(input1, /*key*/ ctx[1]);
    			append_dev(tr, t1);
    			append_dev(tr, th2);
    			append_dev(th2, input2);
    			set_input_value(input2, /*label*/ ctx[2]);
    			append_dev(tr, t2);
    			append_dev(tr, th3);
    			append_dev(th3, input3);
    			set_input_value(input3, /*attr_name*/ ctx[3]);
    			append_dev(th3, t3);
    			append_dev(th3, input4);
    			set_input_value(input4, /*attr_value*/ ctx[4]);

    			if (!mounted) {
    				dispose = [
    					listen_dev(input0, "input", /*input0_input_handler*/ ctx[12]),
    					listen_dev(input1, "input", /*input1_input_handler*/ ctx[13]),
    					listen_dev(input2, "input", /*input2_input_handler*/ ctx[14]),
    					listen_dev(input3, "input", /*input3_input_handler*/ ctx[15]),
    					listen_dev(input4, "input", /*input4_input_handler*/ ctx[16])
    				];

    				mounted = true;
    			}
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*term*/ 1 && input0.value !== /*term*/ ctx[0]) {
    				set_input_value(input0, /*term*/ ctx[0]);
    			}

    			if (dirty & /*key*/ 2 && input1.value !== /*key*/ ctx[1]) {
    				set_input_value(input1, /*key*/ ctx[1]);
    			}

    			if (dirty & /*label*/ 4 && input2.value !== /*label*/ ctx[2]) {
    				set_input_value(input2, /*label*/ ctx[2]);
    			}

    			if (dirty & /*attr_name*/ 8 && input3.value !== /*attr_name*/ ctx[3]) {
    				set_input_value(input3, /*attr_name*/ ctx[3]);
    			}

    			if (dirty & /*attr_value*/ 16 && input4.value !== /*attr_value*/ ctx[4]) {
    				set_input_value(input4, /*attr_value*/ ctx[4]);
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(tr);
    			mounted = false;
    			run_all(dispose);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_2.name,
    		type: "if",
    		source: "(82:4) {#if showFilter}",
    		ctx
    	});

    	return block;
    }

    // (100:16) {#if node.synonyms}
    function create_if_block_1(ctx) {
    	let each_1_anchor;
    	let each_value_2 = /*node*/ ctx[19].synonyms;
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
    			if (dirty & /*data*/ 128) {
    				each_value_2 = /*node*/ ctx[19].synonyms;
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
    		id: create_if_block_1.name,
    		type: "if",
    		source: "(100:16) {#if node.synonyms}",
    		ctx
    	});

    	return block;
    }

    // (101:20) {#each node.synonyms as synonym}
    function create_each_block_2(ctx) {
    	let t_value = /*synonym*/ ctx[25] + "";
    	let t;

    	const block = {
    		c: function create() {
    			t = text(t_value);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, t, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*data*/ 128 && t_value !== (t_value = /*synonym*/ ctx[25] + "")) set_data_dev(t, t_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(t);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block_2.name,
    		type: "each",
    		source: "(101:20) {#each node.synonyms as synonym}",
    		ctx
    	});

    	return block;
    }

    // (111:24) {#if (node[name] != null) && !hide_attrs.includes(name)}
    function create_if_block$1(ctx) {
    	let tr;
    	let td0;
    	let t0_value = /*name*/ ctx[22] + "";
    	let t0;
    	let t1;
    	let t2;
    	let td1;
    	let t3_value = /*node*/ ctx[19][/*name*/ ctx[22]] + "";
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
    			attr_dev(td0, "class", "four wide field_name svelte-1ulg1cd");
    			add_location(td0, file$3, 112, 32, 3096);
    			attr_dev(td1, "class", "twelve wide");
    			add_location(td1, file$3, 113, 32, 3174);
    			attr_dev(tr, "class", "top aligned");
    			add_location(tr, file$3, 111, 28, 3039);
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
    			if (dirty & /*data*/ 128 && t0_value !== (t0_value = /*name*/ ctx[22] + "")) set_data_dev(t0, t0_value);
    			if (dirty & /*data*/ 128 && t3_value !== (t3_value = /*node*/ ctx[19][/*name*/ ctx[22]] + "")) set_data_dev(t3, t3_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(tr);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$1.name,
    		type: "if",
    		source: "(111:24) {#if (node[name] != null) && !hide_attrs.includes(name)}",
    		ctx
    	});

    	return block;
    }

    // (110:20) {#each Object.keys(node) as name}
    function create_each_block_1(ctx) {
    	let show_if = /*node*/ ctx[19][/*name*/ ctx[22]] != null && !/*hide_attrs*/ ctx[8].includes(/*name*/ ctx[22]);
    	let if_block_anchor;
    	let if_block = show_if && create_if_block$1(ctx);

    	const block = {
    		c: function create() {
    			if (if_block) if_block.c();
    			if_block_anchor = empty();
    		},
    		m: function mount(target, anchor) {
    			if (if_block) if_block.m(target, anchor);
    			insert_dev(target, if_block_anchor, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*data*/ 128) show_if = /*node*/ ctx[19][/*name*/ ctx[22]] != null && !/*hide_attrs*/ ctx[8].includes(/*name*/ ctx[22]);

    			if (show_if) {
    				if (if_block) {
    					if_block.p(ctx, dirty);
    				} else {
    					if_block = create_if_block$1(ctx);
    					if_block.c();
    					if_block.m(if_block_anchor.parentNode, if_block_anchor);
    				}
    			} else if (if_block) {
    				if_block.d(1);
    				if_block = null;
    			}
    		},
    		d: function destroy(detaching) {
    			if (if_block) if_block.d(detaching);
    			if (detaching) detach_dev(if_block_anchor);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block_1.name,
    		type: "each",
    		source: "(110:20) {#each Object.keys(node) as name}",
    		ctx
    	});

    	return block;
    }

    // (96:4) {#each data.nodes as node}
    function create_each_block$1(ctx) {
    	let tr;
    	let td0;
    	let t0_value = /*node*/ ctx[19].name + "";
    	let t0;
    	let t1;
    	let t2;
    	let td1;
    	let t3_value = /*node*/ ctx[19].key + "";
    	let t3;
    	let t4;
    	let td2;
    	let t5_value = /*node*/ ctx[19].label + "";
    	let t5;
    	let t6;
    	let td3;
    	let table;
    	let t7;
    	let if_block = /*node*/ ctx[19].synonyms && create_if_block_1(ctx);
    	let each_value_1 = Object.keys(/*node*/ ctx[19]);
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
    			if (if_block) if_block.c();
    			t2 = space();
    			td1 = element("td");
    			t3 = text(t3_value);
    			t4 = space();
    			td2 = element("td");
    			t5 = text(t5_value);
    			t6 = space();
    			td3 = element("td");
    			table = element("table");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			t7 = space();
    			add_location(td0, file$3, 97, 12, 2501);
    			add_location(td1, file$3, 105, 12, 2737);
    			add_location(td2, file$3, 106, 12, 2769);
    			attr_dev(table, "class", "ui compact celled table top aligned");
    			add_location(table, file$3, 108, 16, 2824);
    			add_location(td3, file$3, 107, 12, 2803);
    			add_location(tr, file$3, 96, 8, 2484);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, tr, anchor);
    			append_dev(tr, td0);
    			append_dev(td0, t0);
    			append_dev(td0, t1);
    			if (if_block) if_block.m(td0, null);
    			append_dev(tr, t2);
    			append_dev(tr, td1);
    			append_dev(td1, t3);
    			append_dev(tr, t4);
    			append_dev(tr, td2);
    			append_dev(td2, t5);
    			append_dev(tr, t6);
    			append_dev(tr, td3);
    			append_dev(td3, table);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(table, null);
    			}

    			append_dev(tr, t7);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*data*/ 128 && t0_value !== (t0_value = /*node*/ ctx[19].name + "")) set_data_dev(t0, t0_value);

    			if (/*node*/ ctx[19].synonyms) {
    				if (if_block) {
    					if_block.p(ctx, dirty);
    				} else {
    					if_block = create_if_block_1(ctx);
    					if_block.c();
    					if_block.m(td0, null);
    				}
    			} else if (if_block) {
    				if_block.d(1);
    				if_block = null;
    			}

    			if (dirty & /*data*/ 128 && t3_value !== (t3_value = /*node*/ ctx[19].key + "")) set_data_dev(t3, t3_value);
    			if (dirty & /*data*/ 128 && t5_value !== (t5_value = /*node*/ ctx[19].label + "")) set_data_dev(t5, t5_value);

    			if (dirty & /*data, Object, hide_attrs*/ 384) {
    				each_value_1 = Object.keys(/*node*/ ctx[19]);
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
    			if (if_block) if_block.d();
    			destroy_each(each_blocks, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block$1.name,
    		type: "each",
    		source: "(96:4) {#each data.nodes as node}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$3(ctx) {
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
    	let t3;
    	let th1;
    	let t5;
    	let th2;
    	let t7;
    	let th3;
    	let t9;
    	let t10;
    	let tbody;
    	let current;

    	function select_block_type(ctx, dirty) {
    		if (/*showFilter*/ ctx[6]) return create_if_block_3;
    		return create_else_block$1;
    	}

    	let current_block_type = select_block_type(ctx);
    	let if_block0 = current_block_type(ctx);

    	function pagination_page_binding(value) {
    		/*pagination_page_binding*/ ctx[11].call(null, value);
    	}

    	let pagination_props = {};

    	if (/*page*/ ctx[5] !== void 0) {
    		pagination_props.page = /*page*/ ctx[5];
    	}

    	pagination = new Pagination({ props: pagination_props, $$inline: true });
    	binding_callbacks.push(() => bind(pagination, "page", pagination_page_binding));
    	let if_block1 = /*showFilter*/ ctx[6] && create_if_block_2(ctx);
    	let each_value = /*data*/ ctx[7].nodes;
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block$1(get_each_context$1(ctx, each_value, i));
    	}

    	const block = {
    		c: function create() {
    			div2 = element("div");
    			div0 = element("div");
    			if_block0.c();
    			t0 = space();
    			div1 = element("div");
    			create_component(pagination.$$.fragment);
    			t1 = space();
    			table = element("table");
    			thead = element("thead");
    			tr = element("tr");
    			th0 = element("th");
    			th0.textContent = "Name (Synonyms)";
    			t3 = space();
    			th1 = element("th");
    			th1.textContent = "Key";
    			t5 = space();
    			th2 = element("th");
    			th2.textContent = "Label";
    			t7 = space();
    			th3 = element("th");
    			th3.textContent = "Attributes";
    			t9 = space();
    			if (if_block1) if_block1.c();
    			t10 = space();
    			tbody = element("tbody");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			attr_dev(div0, "class", "eight wide column");
    			add_location(div0, file$3, 47, 4, 1066);
    			attr_dev(div1, "class", "eight wide column right aligned");
    			add_location(div1, file$3, 60, 4, 1489);
    			attr_dev(div2, "class", "ui grid");
    			add_location(div2, file$3, 46, 0, 1040);
    			attr_dev(th0, "class", "two wide");
    			add_location(th0, file$3, 68, 8, 1700);
    			attr_dev(th1, "class", "two wide");
    			add_location(th1, file$3, 71, 8, 1772);
    			attr_dev(th2, "class", "two wide");
    			add_location(th2, file$3, 74, 8, 1832);
    			attr_dev(th3, "class", "four wide");
    			add_location(th3, file$3, 77, 8, 1894);
    			add_location(tr, file$3, 67, 4, 1687);
    			attr_dev(thead, "class", "full-width");
    			add_location(thead, file$3, 66, 4, 1656);
    			add_location(tbody, file$3, 94, 4, 2437);
    			attr_dev(table, "class", "ui compact celled striped table top aligned");
    			add_location(table, file$3, 65, 0, 1592);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div2, anchor);
    			append_dev(div2, div0);
    			if_block0.m(div0, null);
    			append_dev(div2, t0);
    			append_dev(div2, div1);
    			mount_component(pagination, div1, null);
    			insert_dev(target, t1, anchor);
    			insert_dev(target, table, anchor);
    			append_dev(table, thead);
    			append_dev(thead, tr);
    			append_dev(tr, th0);
    			append_dev(tr, t3);
    			append_dev(tr, th1);
    			append_dev(tr, t5);
    			append_dev(tr, th2);
    			append_dev(tr, t7);
    			append_dev(tr, th3);
    			append_dev(thead, t9);
    			if (if_block1) if_block1.m(thead, null);
    			append_dev(table, t10);
    			append_dev(table, tbody);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(tbody, null);
    			}

    			current = true;
    		},
    		p: function update(ctx, [dirty]) {
    			if (current_block_type === (current_block_type = select_block_type(ctx)) && if_block0) {
    				if_block0.p(ctx, dirty);
    			} else {
    				if_block0.d(1);
    				if_block0 = current_block_type(ctx);

    				if (if_block0) {
    					if_block0.c();
    					if_block0.m(div0, null);
    				}
    			}

    			const pagination_changes = {};

    			if (!updating_page && dirty & /*page*/ 32) {
    				updating_page = true;
    				pagination_changes.page = /*page*/ ctx[5];
    				add_flush_callback(() => updating_page = false);
    			}

    			pagination.$set(pagination_changes);

    			if (/*showFilter*/ ctx[6]) {
    				if (if_block1) {
    					if_block1.p(ctx, dirty);
    				} else {
    					if_block1 = create_if_block_2(ctx);
    					if_block1.c();
    					if_block1.m(thead, null);
    				}
    			} else if (if_block1) {
    				if_block1.d(1);
    				if_block1 = null;
    			}

    			if (dirty & /*Object, data, hide_attrs*/ 384) {
    				each_value = /*data*/ ctx[7].nodes;
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context$1(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block$1(child_ctx);
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
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(pagination.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div2);
    			if_block0.d();
    			destroy_component(pagination);
    			if (detaching) detach_dev(t1);
    			if (detaching) detach_dev(table);
    			if (if_block1) if_block1.d();
    			destroy_each(each_blocks, detaching);
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
    	let term = "";
    	let key = "";
    	let label = "";
    	let attr_name = "";
    	let attr_value = "";
    	let page = 0;
    	let showFilter = false;
    	let data = { "nodes": [], "trails": [] };
    	const hide_attrs = ["key", "label", "name", "synonyms"];

    	const onChange = async () => {
    		$$invalidate(5, page = 0);
    		$$invalidate(7, data = await search(term, key, label, attr_name, attr_value, page));
    	};

    	const onChangePage = async () => {
    		$$invalidate(7, data = await search(term, key, label, attr_name, attr_value, page));
    	};

    	const showFilters = () => {
    		$$invalidate(6, showFilter = true);
    	};

    	const clearFilters = () => {
    		$$invalidate(0, term = "");
    		$$invalidate(1, key = "");
    		$$invalidate(2, label = "");
    		$$invalidate(3, attr_name = "");
    		$$invalidate(4, attr_value = "");
    		$$invalidate(5, page = 0);
    		$$invalidate(6, showFilter = false);
    	};

    	const writable_props = [];

    	Object_1.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<Admin> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("Admin", $$slots, []);

    	function pagination_page_binding(value) {
    		page = value;
    		$$invalidate(5, page);
    	}

    	function input0_input_handler() {
    		term = this.value;
    		$$invalidate(0, term);
    	}

    	function input1_input_handler() {
    		key = this.value;
    		$$invalidate(1, key);
    	}

    	function input2_input_handler() {
    		label = this.value;
    		$$invalidate(2, label);
    	}

    	function input3_input_handler() {
    		attr_name = this.value;
    		$$invalidate(3, attr_name);
    	}

    	function input4_input_handler() {
    		attr_value = this.value;
    		$$invalidate(4, attr_value);
    	}

    	$$self.$capture_state = () => ({
    		search,
    		Pagination,
    		term,
    		key,
    		label,
    		attr_name,
    		attr_value,
    		page,
    		showFilter,
    		data,
    		hide_attrs,
    		onChange,
    		onChangePage,
    		showFilters,
    		clearFilters
    	});

    	$$self.$inject_state = $$props => {
    		if ("term" in $$props) $$invalidate(0, term = $$props.term);
    		if ("key" in $$props) $$invalidate(1, key = $$props.key);
    		if ("label" in $$props) $$invalidate(2, label = $$props.label);
    		if ("attr_name" in $$props) $$invalidate(3, attr_name = $$props.attr_name);
    		if ("attr_value" in $$props) $$invalidate(4, attr_value = $$props.attr_value);
    		if ("page" in $$props) $$invalidate(5, page = $$props.page);
    		if ("showFilter" in $$props) $$invalidate(6, showFilter = $$props.showFilter);
    		if ("data" in $$props) $$invalidate(7, data = $$props.data);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*term*/ 1) {
    			 onChange();
    		}

    		if ($$self.$$.dirty & /*key*/ 2) {
    			 onChange();
    		}

    		if ($$self.$$.dirty & /*label*/ 4) {
    			 onChange();
    		}

    		if ($$self.$$.dirty & /*attr_name*/ 8) {
    			 onChange();
    		}

    		if ($$self.$$.dirty & /*attr_value*/ 16) {
    			 onChange();
    		}

    		if ($$self.$$.dirty & /*page*/ 32) {
    			 onChangePage();
    		}
    	};

    	return [
    		term,
    		key,
    		label,
    		attr_name,
    		attr_value,
    		page,
    		showFilter,
    		data,
    		hide_attrs,
    		showFilters,
    		clearFilters,
    		pagination_page_binding,
    		input0_input_handler,
    		input1_input_handler,
    		input2_input_handler,
    		input3_input_handler,
    		input4_input_handler
    	];
    }

    class Admin extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$3, create_fragment$3, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "Admin",
    			options,
    			id: create_fragment$3.name
    		});
    	}
    }

    /* src/App.svelte generated by Svelte v3.24.1 */
    const file$4 = "src/App.svelte";

    // (20:34) 
    function create_if_block_3$1(ctx) {
    	let iframe;
    	let iframe_src_value;

    	const block = {
    		c: function create() {
    			iframe = element("iframe");
    			if (iframe.src !== (iframe_src_value = "https://www.entitykb.org/")) attr_dev(iframe, "src", iframe_src_value);
    			attr_dev(iframe, "class", "svelte-jbahxs");
    			add_location(iframe, file$4, 20, 8, 500);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, iframe, anchor);
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(iframe);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_3$1.name,
    		type: "if",
    		source: "(20:34) ",
    		ctx
    	});

    	return block;
    }

    // (18:34) 
    function create_if_block_2$1(ctx) {
    	let iframe;
    	let iframe_src_value;

    	const block = {
    		c: function create() {
    			iframe = element("iframe");
    			if (iframe.src !== (iframe_src_value = "https://www.entitykb.org/")) attr_dev(iframe, "src", iframe_src_value);
    			attr_dev(iframe, "class", "svelte-jbahxs");
    			add_location(iframe, file$4, 18, 8, 407);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, iframe, anchor);
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(iframe);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_2$1.name,
    		type: "if",
    		source: "(18:34) ",
    		ctx
    	});

    	return block;
    }

    // (16:33) 
    function create_if_block_1$1(ctx) {
    	let iframe;
    	let iframe_src_value;

    	const block = {
    		c: function create() {
    			iframe = element("iframe");
    			if (iframe.src !== (iframe_src_value = "/docs")) attr_dev(iframe, "src", iframe_src_value);
    			attr_dev(iframe, "class", "svelte-jbahxs");
    			add_location(iframe, file$4, 16, 8, 334);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, iframe, anchor);
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(iframe);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_1$1.name,
    		type: "if",
    		source: "(16:33) ",
    		ctx
    	});

    	return block;
    }

    // (12:4) {#if (choice === "admin")}
    function create_if_block$2(ctx) {
    	let div;
    	let admin;
    	let current;
    	admin = new Admin({ $$inline: true });

    	const block = {
    		c: function create() {
    			div = element("div");
    			create_component(admin.$$.fragment);
    			attr_dev(div, "id", "content");
    			attr_dev(div, "class", "svelte-jbahxs");
    			add_location(div, file$4, 12, 4, 244);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			mount_component(admin, div, null);
    			current = true;
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(admin.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(admin.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    			destroy_component(admin);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$2.name,
    		type: "if",
    		source: "(12:4) {#if (choice === \\\"admin\\\")}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$4(ctx) {
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
    		/*menu_choice_binding*/ ctx[1].call(null, value);
    	}

    	let menu_props = {};

    	if (/*choice*/ ctx[0] !== void 0) {
    		menu_props.choice = /*choice*/ ctx[0];
    	}

    	menu = new Menu({ props: menu_props, $$inline: true });
    	binding_callbacks.push(() => bind(menu, "choice", menu_choice_binding));
    	const if_block_creators = [create_if_block$2, create_if_block_1$1, create_if_block_2$1, create_if_block_3$1];
    	const if_blocks = [];

    	function select_block_type(ctx, dirty) {
    		if (/*choice*/ ctx[0] === "admin") return 0;
    		if (/*choice*/ ctx[0] === "api") return 1;
    		if (/*choice*/ ctx[0] === "docs") return 2;
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
    			add_location(main, file$4, 8, 0, 167);
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

    			if (current_block_type_index !== previous_block_index) {
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
    		id: create_fragment$4.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$4($$self, $$props, $$invalidate) {
    	let choice = "admin";
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

    	$$self.$capture_state = () => ({ Menu, Bottom, Admin, choice });

    	$$self.$inject_state = $$props => {
    		if ("choice" in $$props) $$invalidate(0, choice = $$props.choice);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	return [choice, menu_choice_binding];
    }

    class App extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$4, create_fragment$4, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "App",
    			options,
    			id: create_fragment$4.name
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
