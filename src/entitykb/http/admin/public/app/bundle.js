
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
    const getURL = baseURL + "/nodes/";
    const pageSize = 10;

    const getNodes = async (q, page, filters) => {
        let traversal = [];

        function addFieldFilter(field) {
            let value = filters[field];

            if (field && value) {
                if (field === "attributes") ; else {
                    traversal.push({
                        "criteria": [
                            {
                                "type": "field",
                                "field": field,
                                "compare": "icontains",
                                "value": value,
                            }
                        ]
                    });
                }
            }
        }

        Object.keys(filters).forEach(addFieldFilter);

        const body = {
            q: q,
            limit: pageSize,
            offset: page * pageSize,
            traversal: traversal,
        };

        return await callSearch(searchURL, "POST", body);
    };

    const getEdges = async (key, page) => {
        const body = {
            q: key,
            input: 'key',
            traversal: [
                {
                    directions: ['incoming', 'outgoing'],
                    max_hops: 1,
                }
            ],
            limit: pageSize,
            offset: page * pageSize,
        };
        return await callSearch(searchURL, "POST", body);
    };


    const getNode = async (key) => {
        return await callSearch(getURL + key, "GET", null);
    };

    const callSearch = async (url, method, body) => {
        if (body) {
            body = JSON.stringify(body);
        }

        return await fetch(url, {
            method: method,
            mode: 'cors',
            cache: 'no-cache',
            credentials: 'same-origin',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json',
            },
            redirect: 'follow',
            referrerPolicy: 'no-referrer',
            body: body,
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

    /* src/ColumnFilter.svelte generated by Svelte v3.24.1 */
    const file$3 = "src/ColumnFilter.svelte";

    function get_each_context$1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[10] = list[i];
    	return child_ctx;
    }

    // (40:4) {:else}
    function create_else_block_1(ctx) {
    	let a;
    	let i;
    	let t0;
    	let t1;
    	let t2;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			a = element("a");
    			i = element("i");
    			t0 = space();
    			t1 = text(/*display*/ ctx[0]);
    			t2 = text("\n         ");
    			attr_dev(i, "class", "blue filter icon svelte-1f5zqhf");
    			add_location(i, file$3, 41, 12, 1100);
    			attr_dev(a, "class", "clickable");
    			add_location(a, file$3, 40, 8, 1044);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, a, anchor);
    			append_dev(a, i);
    			append_dev(a, t0);
    			append_dev(a, t1);
    			insert_dev(target, t2, anchor);

    			if (!mounted) {
    				dispose = listen_dev(a, "click", /*openFilter*/ ctx[5], false, false, false);
    				mounted = true;
    			}
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*display*/ 1) set_data_dev(t1, /*display*/ ctx[0]);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(a);
    			if (detaching) detach_dev(t2);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block_1.name,
    		type: "else",
    		source: "(40:4) {:else}",
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
    		if (/*options*/ ctx[1]) return create_if_block_1;
    		return create_else_block$1;
    	}

    	let current_block_type = select_block_type_1(ctx);
    	let if_block = current_block_type(ctx);

    	const block = {
    		c: function create() {
    			a = element("a");
    			i = element("i");
    			t = text("\n         \n        ");
    			if_block.c();
    			if_block_anchor = empty();
    			attr_dev(i, "class", "red window close icon svelte-1f5zqhf");
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
    		id: create_if_block$1.name,
    		type: "if",
    		source: "(25:4) {#if inFilterMode}",
    		ctx
    	});

    	return block;
    }

    // (37:8) {:else}
    function create_else_block$1(ctx) {
    	let input;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			input = element("input");
    			attr_dev(input, "placeholder", /*display*/ ctx[0]);
    			input.autofocus = true;
    			add_location(input, file$3, 37, 12, 943);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, input, anchor);
    			set_input_value(input, /*filterValue*/ ctx[2]);
    			input.focus();

    			if (!mounted) {
    				dispose = listen_dev(input, "input", /*input_input_handler*/ ctx[8]);
    				mounted = true;
    			}
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*display*/ 1) {
    				attr_dev(input, "placeholder", /*display*/ ctx[0]);
    			}

    			if (dirty & /*filterValue, options*/ 6 && input.value !== /*filterValue*/ ctx[2]) {
    				set_input_value(input, /*filterValue*/ ctx[2]);
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
    		source: "(37:8) {:else}",
    		ctx
    	});

    	return block;
    }

    // (30:8) {#if options}
    function create_if_block_1(ctx) {
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
    		each_blocks[i] = create_each_block$1(get_each_context$1(ctx, each_value, i));
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
    			add_location(option, file$3, 31, 16, 750);
    			if (/*filterValue*/ ctx[2] === void 0) add_render_callback(() => /*select_change_handler*/ ctx[7].call(select));
    			add_location(select, file$3, 30, 12, 700);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, select, anchor);
    			append_dev(select, option);
    			append_dev(option, t0);
    			append_dev(option, t1);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(select, null);
    			}

    			select_option(select, /*filterValue*/ ctx[2]);

    			if (!mounted) {
    				dispose = listen_dev(select, "change", /*select_change_handler*/ ctx[7]);
    				mounted = true;
    			}
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*display*/ 1) set_data_dev(t1, /*display*/ ctx[0]);

    			if (dirty & /*options*/ 2) {
    				each_value = /*options*/ ctx[1];
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

    			if (dirty & /*filterValue, options*/ 6) {
    				select_option(select, /*filterValue*/ ctx[2]);
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
    		source: "(30:8) {#if options}",
    		ctx
    	});

    	return block;
    }

    // (33:12) {#each options as option}
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
    			add_location(option, file$3, 33, 16, 847);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, option, anchor);
    			append_dev(option, t);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*options*/ 2 && t_value !== (t_value = /*option*/ ctx[10] + "")) set_data_dev(t, t_value);

    			if (dirty & /*options*/ 2 && option_value_value !== (option_value_value = /*option*/ ctx[10])) {
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
    		source: "(33:12) {#each options as option}",
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
    	let { display = null } = $$props;
    	let { options = "" } = $$props;
    	let filterValue = "";
    	let inFilterMode = false;

    	const cancelFilter = () => {
    		$$invalidate(3, inFilterMode = false);
    		$$invalidate(2, filterValue = "");
    	};

    	const openFilter = () => {
    		$$invalidate(3, inFilterMode = true);
    	};

    	const writable_props = ["name", "display", "options"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<ColumnFilter> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("ColumnFilter", $$slots, []);

    	function select_change_handler() {
    		filterValue = select_value(this);
    		$$invalidate(2, filterValue);
    		$$invalidate(1, options);
    	}

    	function input_input_handler() {
    		filterValue = this.value;
    		$$invalidate(2, filterValue);
    		$$invalidate(1, options);
    	}

    	$$self.$$set = $$props => {
    		if ("name" in $$props) $$invalidate(6, name = $$props.name);
    		if ("display" in $$props) $$invalidate(0, display = $$props.display);
    		if ("options" in $$props) $$invalidate(1, options = $$props.options);
    	};

    	$$self.$capture_state = () => ({
    		createEventDispatcher,
    		dispatch,
    		name,
    		display,
    		options,
    		filterValue,
    		inFilterMode,
    		cancelFilter,
    		openFilter
    	});

    	$$self.$inject_state = $$props => {
    		if ("name" in $$props) $$invalidate(6, name = $$props.name);
    		if ("display" in $$props) $$invalidate(0, display = $$props.display);
    		if ("options" in $$props) $$invalidate(1, options = $$props.options);
    		if ("filterValue" in $$props) $$invalidate(2, filterValue = $$props.filterValue);
    		if ("inFilterMode" in $$props) $$invalidate(3, inFilterMode = $$props.inFilterMode);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*name, filterValue*/ 68) {
    			 dispatch("update", { name, "value": filterValue });
    		}
    	};

    	return [
    		display,
    		options,
    		filterValue,
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
    		init(this, options, instance$3, create_fragment$3, safe_not_equal, { name: 6, display: 0, options: 1 });

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

    // (34:4) {:else}
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
    			t = text("\n         \n        Attributes");
    			attr_dev(i, "class", "blue filter icon svelte-1ds6of5");
    			add_location(i, file$4, 34, 33, 854);
    			add_location(a, file$4, 34, 8, 829);
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
    		source: "(34:4) {:else}",
    		ctx
    	});

    	return block;
    }

    // (28:4) {#if inFilterMode}
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
    			t0 = text("\n         \n        ");
    			input0 = element("input");
    			t1 = text("\n        ≈\n        ");
    			input1 = element("input");
    			attr_dev(i, "class", "red window close icon svelte-1ds6of5");
    			add_location(i, file$4, 28, 35, 612);
    			add_location(a, file$4, 28, 8, 585);
    			attr_dev(input0, "placeholder", "name");
    			input0.autofocus = true;
    			add_location(input0, file$4, 30, 8, 677);
    			attr_dev(input1, "placeholder", "value");
    			add_location(input1, file$4, 32, 8, 762);
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
    		source: "(28:4) {#if inFilterMode}",
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
    			add_location(div, file$4, 26, 0, 536);
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
    		dispatch("update", { name, value });
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
    		if ($$self.$$.dirty & /*name*/ 1) {
    			 updateFilterValue();
    		}

    		if ($$self.$$.dirty & /*value*/ 2) {
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

    function get_each_context_1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[16] = list[i];
    	return child_ctx;
    }

    function get_each_context$2(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[13] = list[i];
    	return child_ctx;
    }

    // (111:20) {#each iterateAttrs(node) as kv}
    function create_each_block_1(ctx) {
    	let tr;
    	let td0;
    	let t0_value = /*kv*/ ctx[16][0] + "";
    	let t0;
    	let t1;
    	let t2;
    	let td1;
    	let t3_value = /*kv*/ ctx[16][1] + "";
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
    			add_location(td0, file$5, 112, 28, 3047);
    			attr_dev(td1, "class", "twelve wide");
    			add_location(td1, file$5, 113, 28, 3122);
    			attr_dev(tr, "class", "top aligned");
    			add_location(tr, file$5, 111, 24, 2994);
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
    			if (dirty & /*data*/ 2 && t0_value !== (t0_value = /*kv*/ ctx[16][0] + "")) set_data_dev(t0, t0_value);
    			if (dirty & /*data*/ 2 && t3_value !== (t3_value = /*kv*/ ctx[16][1] + "")) set_data_dev(t3, t3_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(tr);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block_1.name,
    		type: "each",
    		source: "(111:20) {#each iterateAttrs(node) as kv}",
    		ctx
    	});

    	return block;
    }

    // (104:4) {#each data.nodes as node}
    function create_each_block$2(ctx) {
    	let tr;
    	let td0;
    	let t0_value = /*node*/ ctx[13].name + "";
    	let t0;
    	let t1;
    	let td1;
    	let t2_value = /*node*/ ctx[13].key + "";
    	let t2;
    	let t3;
    	let td2;
    	let t4_value = /*node*/ ctx[13].label + "";
    	let t4;
    	let t5;
    	let td3;
    	let table;
    	let t6;
    	let mounted;
    	let dispose;
    	let each_value_1 = /*iterateAttrs*/ ctx[6](/*node*/ ctx[13]);
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
    			add_location(td0, file$5, 105, 12, 2745);
    			add_location(td1, file$5, 106, 12, 2778);
    			add_location(td2, file$5, 107, 12, 2810);
    			attr_dev(table, "class", "ui compact celled table top aligned");
    			add_location(table, file$5, 109, 16, 2865);
    			add_location(td3, file$5, 108, 12, 2844);
    			add_location(tr, file$5, 104, 8, 2699);
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
    						if (is_function(/*openRow*/ ctx[5](/*node*/ ctx[13].key))) /*openRow*/ ctx[5](/*node*/ ctx[13].key).apply(this, arguments);
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
    			if (dirty & /*data*/ 2 && t0_value !== (t0_value = /*node*/ ctx[13].name + "")) set_data_dev(t0, t0_value);
    			if (dirty & /*data*/ 2 && t2_value !== (t2_value = /*node*/ ctx[13].key + "")) set_data_dev(t2, t2_value);
    			if (dirty & /*data*/ 2 && t4_value !== (t4_value = /*node*/ ctx[13].label + "")) set_data_dev(t4, t4_value);

    			if (dirty & /*iterateAttrs, data*/ 66) {
    				each_value_1 = /*iterateAttrs*/ ctx[6](/*node*/ ctx[13]);
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
    		source: "(104:4) {#each data.nodes as node}",
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
    		/*pagination_page_binding*/ ctx[8].call(null, value);
    	}

    	let pagination_props = {};

    	if (/*page*/ ctx[0] !== void 0) {
    		pagination_props.page = /*page*/ ctx[0];
    	}

    	pagination = new Pagination({ props: pagination_props, $$inline: true });
    	binding_callbacks.push(() => bind(pagination, "page", pagination_page_binding));

    	columnfilter0 = new ColumnFilter({
    			props: { name: "name", display: "Name" },
    			$$inline: true
    		});

    	columnfilter0.$on("update", /*onUpdateName*/ ctx[3]);

    	columnfilter1 = new ColumnFilter({
    			props: { name: "key", display: "Key" },
    			$$inline: true
    		});

    	columnfilter1.$on("update", /*onUpdate*/ ctx[4]);

    	columnfilter2 = new ColumnFilter({
    			props: {
    				name: "label",
    				display: "Label",
    				options: /*labels*/ ctx[2]
    			},
    			$$inline: true
    		});

    	columnfilter2.$on("update", /*onUpdate*/ ctx[4]);
    	attributefilter = new AttributeFilter({ $$inline: true });
    	attributefilter.$on("update", /*onUpdate*/ ctx[4]);
    	let each_value = /*data*/ ctx[1].nodes;
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
    			add_location(div0, file$5, 78, 4, 1881);
    			attr_dev(div1, "class", "eight wide column right aligned");
    			add_location(div1, file$5, 80, 4, 1928);
    			attr_dev(div2, "class", "ui grid");
    			add_location(div2, file$5, 77, 0, 1855);
    			attr_dev(th0, "class", "two wide");
    			add_location(th0, file$5, 88, 8, 2151);
    			attr_dev(th1, "class", "two wide");
    			add_location(th1, file$5, 91, 8, 2276);
    			attr_dev(th2, "class", "two wide");
    			add_location(th2, file$5, 94, 8, 2395);
    			attr_dev(th3, "class", "four wide");
    			add_location(th3, file$5, 97, 8, 2535);
    			add_location(tr, file$5, 87, 4, 2138);
    			attr_dev(thead, "class", "full-width");
    			add_location(thead, file$5, 86, 4, 2107);
    			add_location(tbody, file$5, 102, 4, 2652);
    			attr_dev(table, "class", "ui compact selectable celled striped table top aligned");
    			add_location(table, file$5, 85, 0, 2032);
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

    			if (!updating_page && dirty & /*page*/ 1) {
    				updating_page = true;
    				pagination_changes.page = /*page*/ ctx[0];
    				add_flush_callback(() => updating_page = false);
    			}

    			pagination.$set(pagination_changes);

    			if (dirty & /*openRow, data, iterateAttrs*/ 98) {
    				each_value = /*data*/ ctx[1].nodes;
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
    	let { selectKey = null } = $$props;
    	let q = "";
    	let page = 0;
    	let filters = { "name": "", "key": "", "label": "" };
    	let data = { "nodes": [], "trails": [] };
    	let labels = ["COUNTRY", "CONTINENT", "DIVISION"];

    	const isAttribute = fieldName => {
    		return !["key", "name", "label"].includes(fieldName);
    	};

    	const onUpdateName = async event => {
    		$$invalidate(9, q = event.detail.value);
    	};

    	const onUpdate = async event => {
    		if (isAttribute(event.detail.name)) {
    			$$invalidate(10, filters = {
    				"name": filters["name"],
    				"key": filters["key"],
    				"label": filters["label"]
    			});

    			if (event.detail.name && event.detail.value) {
    				$$invalidate(10, filters[event.detail.name] = event.detail.value, filters);
    			}
    		} else {
    			$$invalidate(10, filters[event.detail.name] = event.detail.value, filters);
    		}

    		$$invalidate(0, page = 0);
    	};

    	const reloadData = async () => {
    		$$invalidate(1, data = await getNodes(q, page, filters));
    	};

    	const openRow = key => {
    		$$invalidate(7, selectKey = key);
    	};

    	const iterateAttrs = node => {
    		let attrs = [];
    		const names = Object.keys(node);

    		for (let index = 0; index < names.length; ++index) {
    			let name = names[index];
    			if (!isAttribute(name)) continue;
    			let value = node[name];
    			if (!Boolean(value)) continue;
    			if (value instanceof Array && value.length === 0) continue;
    			attrs.push([name, value]);
    		}

    		return attrs;
    	};

    	const writable_props = ["selectKey"];

    	Object_1.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<ListView> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("ListView", $$slots, []);

    	function pagination_page_binding(value) {
    		page = value;
    		$$invalidate(0, page);
    	}

    	$$self.$$set = $$props => {
    		if ("selectKey" in $$props) $$invalidate(7, selectKey = $$props.selectKey);
    	};

    	$$self.$capture_state = () => ({
    		getNodes,
    		Pagination,
    		ColumnFilter,
    		AttributeFilter,
    		selectKey,
    		q,
    		page,
    		filters,
    		data,
    		labels,
    		isAttribute,
    		onUpdateName,
    		onUpdate,
    		reloadData,
    		openRow,
    		iterateAttrs
    	});

    	$$self.$inject_state = $$props => {
    		if ("selectKey" in $$props) $$invalidate(7, selectKey = $$props.selectKey);
    		if ("q" in $$props) $$invalidate(9, q = $$props.q);
    		if ("page" in $$props) $$invalidate(0, page = $$props.page);
    		if ("filters" in $$props) $$invalidate(10, filters = $$props.filters);
    		if ("data" in $$props) $$invalidate(1, data = $$props.data);
    		if ("labels" in $$props) $$invalidate(2, labels = $$props.labels);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*q, page, filters*/ 1537) {
    			 reloadData();
    		}
    	};

    	return [
    		page,
    		data,
    		labels,
    		onUpdateName,
    		onUpdate,
    		openRow,
    		iterateAttrs,
    		selectKey,
    		pagination_page_binding
    	];
    }

    class ListView extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$5, create_fragment$5, safe_not_equal, { selectKey: 7 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "ListView",
    			options,
    			id: create_fragment$5.name
    		});
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
    	child_ctx[10] = list[i];
    	return child_ctx;
    }

    function get_each_context_1$1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[13] = list[i];
    	return child_ctx;
    }

    // (72:16) {#if isAttribute(fieldName) && Boolean(node[fieldName])}
    function create_if_block$3(ctx) {
    	let tr;
    	let td0;
    	let t0_value = /*fieldName*/ ctx[13] + "";
    	let t0;
    	let t1;
    	let td1;
    	let t2_value = /*node*/ ctx[0][/*fieldName*/ ctx[13]] + "";
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
    			add_location(td0, file$6, 73, 24, 1997);
    			add_location(td1, file$6, 74, 24, 2042);
    			add_location(tr, file$6, 72, 20, 1968);
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
    			if (dirty & /*node*/ 1 && t0_value !== (t0_value = /*fieldName*/ ctx[13] + "")) set_data_dev(t0, t0_value);
    			if (dirty & /*node*/ 1 && t2_value !== (t2_value = /*node*/ ctx[0][/*fieldName*/ ctx[13]] + "")) set_data_dev(t2, t2_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(tr);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$3.name,
    		type: "if",
    		source: "(72:16) {#if isAttribute(fieldName) && Boolean(node[fieldName])}",
    		ctx
    	});

    	return block;
    }

    // (71:12) {#each Object.keys(node) as fieldName}
    function create_each_block_1$1(ctx) {
    	let show_if = /*isAttribute*/ ctx[3](/*fieldName*/ ctx[13]) && Boolean(/*node*/ ctx[0][/*fieldName*/ ctx[13]]);
    	let if_block_anchor;
    	let if_block = show_if && create_if_block$3(ctx);

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
    			if (dirty & /*node*/ 1) show_if = /*isAttribute*/ ctx[3](/*fieldName*/ ctx[13]) && Boolean(/*node*/ ctx[0][/*fieldName*/ ctx[13]]);

    			if (show_if) {
    				if (if_block) {
    					if_block.p(ctx, dirty);
    				} else {
    					if_block = create_if_block$3(ctx);
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
    		id: create_each_block_1$1.name,
    		type: "each",
    		source: "(71:12) {#each Object.keys(node) as fieldName}",
    		ctx
    	});

    	return block;
    }

    // (102:12) {#each edges as edge}
    function create_each_block$3(ctx) {
    	let tr;
    	let td0;
    	let t0_value = /*edge*/ ctx[10].direction + "";
    	let t0;
    	let t1;
    	let td1;
    	let t2_value = /*edge*/ ctx[10].verb + "";
    	let t2;
    	let t3;
    	let td2;
    	let t4_value = /*edge*/ ctx[10].name + "";
    	let t4;
    	let t5;
    	let td3;
    	let t6_value = /*edge*/ ctx[10].label + "";
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
    			add_location(td0, file$6, 103, 20, 2963);
    			add_location(td1, file$6, 104, 20, 3009);
    			add_location(td2, file$6, 105, 20, 3050);
    			add_location(td3, file$6, 106, 20, 3091);
    			add_location(tr, file$6, 102, 16, 2909);
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
    						if (is_function(/*openRow*/ ctx[4](/*edge*/ ctx[10].key))) /*openRow*/ ctx[4](/*edge*/ ctx[10].key).apply(this, arguments);
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
    			if (dirty & /*edges*/ 2 && t0_value !== (t0_value = /*edge*/ ctx[10].direction + "")) set_data_dev(t0, t0_value);
    			if (dirty & /*edges*/ 2 && t2_value !== (t2_value = /*edge*/ ctx[10].verb + "")) set_data_dev(t2, t2_value);
    			if (dirty & /*edges*/ 2 && t4_value !== (t4_value = /*edge*/ ctx[10].name + "")) set_data_dev(t4, t4_value);
    			if (dirty & /*edges*/ 2 && t6_value !== (t6_value = /*edge*/ ctx[10].label + "")) set_data_dev(t6, t6_value);
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
    		source: "(102:12) {#each edges as edge}",
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
    	let t4_value = /*node*/ ctx[0]["key"] + "";
    	let t4;
    	let t5;
    	let tr1;
    	let td2;
    	let t7;
    	let td3;
    	let t8_value = /*node*/ ctx[0]["name"] + "";
    	let t8;
    	let t9;
    	let tr2;
    	let td4;
    	let t11;
    	let td5;
    	let t12_value = /*node*/ ctx[0]["label"] + "";
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
    	let t19;
    	let th1;
    	let t21;
    	let th2;
    	let t23;
    	let th3;
    	let t25;
    	let tbody1;
    	let current;
    	let each_value_1 = Object.keys(/*node*/ ctx[0]);
    	validate_each_argument(each_value_1);
    	let each_blocks_1 = [];

    	for (let i = 0; i < each_value_1.length; i += 1) {
    		each_blocks_1[i] = create_each_block_1$1(get_each_context_1$1(ctx, each_value_1, i));
    	}

    	function pagination_page_binding(value) {
    		/*pagination_page_binding*/ ctx[6].call(null, value);
    	}

    	let pagination_props = {};

    	if (/*page*/ ctx[2] !== void 0) {
    		pagination_props.page = /*page*/ ctx[2];
    	}

    	pagination = new Pagination({ props: pagination_props, $$inline: true });
    	binding_callbacks.push(() => bind(pagination, "page", pagination_page_binding));
    	let each_value = /*edges*/ ctx[1];
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
    			th0.textContent = "Direction";
    			t19 = space();
    			th1 = element("th");
    			th1.textContent = "Verb";
    			t21 = space();
    			th2 = element("th");
    			th2.textContent = "Name";
    			t23 = space();
    			th3 = element("th");
    			th3.textContent = "Label";
    			t25 = space();
    			tbody1 = element("tbody");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			add_location(h30, file$6, 55, 8, 1366);
    			attr_dev(td0, "class", "two wide column");
    			add_location(td0, file$6, 59, 16, 1493);
    			attr_dev(td1, "class", "five wide column");
    			add_location(td1, file$6, 60, 16, 1546);
    			add_location(tr0, file$6, 58, 12, 1472);
    			add_location(td2, file$6, 63, 16, 1645);
    			add_location(td3, file$6, 64, 16, 1675);
    			add_location(tr1, file$6, 62, 12, 1624);
    			add_location(td4, file$6, 67, 16, 1750);
    			add_location(td5, file$6, 68, 16, 1781);
    			add_location(tr2, file$6, 66, 12, 1729);
    			add_location(tbody0, file$6, 57, 12, 1452);
    			attr_dev(table0, "class", "ui compact definition table");
    			add_location(table0, file$6, 56, 8, 1396);
    			attr_dev(div0, "class", "seven wide column");
    			add_location(div0, file$6, 54, 4, 1326);
    			add_location(h31, file$6, 84, 16, 2309);
    			attr_dev(div1, "class", "one wide column");
    			add_location(div1, file$6, 83, 12, 2263);
    			attr_dev(div2, "class", "fifteen wide column right aligned");
    			add_location(div2, file$6, 86, 12, 2363);
    			attr_dev(div3, "class", "ui grid");
    			add_location(div3, file$6, 82, 8, 2229);
    			attr_dev(th0, "class", "one wide");
    			add_location(th0, file$6, 94, 16, 2621);
    			attr_dev(th1, "class", "one wide");
    			add_location(th1, file$6, 95, 16, 2673);
    			attr_dev(th2, "class", "four wide");
    			add_location(th2, file$6, 96, 16, 2720);
    			attr_dev(th3, "class", "two wide");
    			add_location(th3, file$6, 97, 16, 2768);
    			add_location(tr3, file$6, 93, 12, 2600);
    			attr_dev(thead, "class", "full-width");
    			add_location(thead, file$6, 92, 12, 2561);
    			add_location(tbody1, file$6, 100, 12, 2851);
    			attr_dev(table1, "class", "ui compact striped celled table");
    			add_location(table1, file$6, 91, 8, 2501);
    			attr_dev(div4, "class", "nine wide column");
    			add_location(div4, file$6, 81, 4, 2190);
    			attr_dev(div5, "class", "ui grid");
    			add_location(div5, file$6, 53, 0, 1300);
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
    			append_dev(tr3, t19);
    			append_dev(tr3, th1);
    			append_dev(tr3, t21);
    			append_dev(tr3, th2);
    			append_dev(tr3, t23);
    			append_dev(tr3, th3);
    			append_dev(table1, t25);
    			append_dev(table1, tbody1);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(tbody1, null);
    			}

    			current = true;
    		},
    		p: function update(ctx, [dirty]) {
    			if ((!current || dirty & /*node*/ 1) && t4_value !== (t4_value = /*node*/ ctx[0]["key"] + "")) set_data_dev(t4, t4_value);
    			if ((!current || dirty & /*node*/ 1) && t8_value !== (t8_value = /*node*/ ctx[0]["name"] + "")) set_data_dev(t8, t8_value);
    			if ((!current || dirty & /*node*/ 1) && t12_value !== (t12_value = /*node*/ ctx[0]["label"] + "")) set_data_dev(t12, t12_value);

    			if (dirty & /*node, Object, isAttribute, Boolean*/ 9) {
    				each_value_1 = Object.keys(/*node*/ ctx[0]);
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

    			if (dirty & /*openRow, edges*/ 18) {
    				each_value = /*edges*/ ctx[1];
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
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(pagination.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div5);
    			destroy_each(each_blocks_1, detaching);
    			destroy_component(pagination);
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
    	let { key = null } = $$props;
    	let node = {};
    	let edges = [];
    	let page = 0;
    	let relationships = new Map();

    	function addTrail(trail) {
    		let neighbor = relationships.get(trail.end);

    		function addEdge(edge) {
    			const dir = edge.end === trail.end ? "outgoing" : "incoming";

    			$$invalidate(1, edges = [
    				...edges,
    				{
    					direction: dir,
    					verb: edge.verb,
    					key: neighbor.key,
    					label: neighbor.label,
    					name: neighbor.name
    				}
    			]);
    		}

    		trail && trail.hops && trail.hops[0].edges.forEach(addEdge);
    	}

    	const onChange = async () => {
    		$$invalidate(0, node = await getNode(key));
    		$$invalidate(1, edges = []);
    		let result = await getEdges(key, page);

    		result.nodes.forEach(n => {
    			relationships.set(n.key, n);
    		});

    		result.trails.forEach(addTrail);
    		$$invalidate(1, edges);
    	};

    	const isAttribute = fieldName => {
    		return !["key", "name", "label"].includes(fieldName);
    	};

    	const openRow = rowKey => {
    		$$invalidate(5, key = rowKey);
    	};

    	const writable_props = ["key"];

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
    		if ("key" in $$props) $$invalidate(5, key = $$props.key);
    	};

    	$$self.$capture_state = () => ({
    		getNode,
    		getEdges,
    		Pagination,
    		key,
    		node,
    		edges,
    		page,
    		relationships,
    		addTrail,
    		onChange,
    		isAttribute,
    		openRow
    	});

    	$$self.$inject_state = $$props => {
    		if ("key" in $$props) $$invalidate(5, key = $$props.key);
    		if ("node" in $$props) $$invalidate(0, node = $$props.node);
    		if ("edges" in $$props) $$invalidate(1, edges = $$props.edges);
    		if ("page" in $$props) $$invalidate(2, page = $$props.page);
    		if ("relationships" in $$props) relationships = $$props.relationships;
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*key, page*/ 36) {
    			 onChange();
    		}
    	};

    	return [node, edges, page, isAttribute, openRow, key, pagination_page_binding];
    }

    class DetailView extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$6, create_fragment$6, safe_not_equal, { key: 5 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "DetailView",
    			options,
    			id: create_fragment$6.name
    		});
    	}

    	get key() {
    		throw new Error("<DetailView>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set key(value) {
    		throw new Error("<DetailView>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/App.svelte generated by Svelte v3.24.1 */
    const file$7 = "src/App.svelte";

    // (41:34) 
    function create_if_block_3(ctx) {
    	let iframe;
    	let iframe_src_value;

    	const block = {
    		c: function create() {
    			iframe = element("iframe");
    			attr_dev(iframe, "title", "Docs");
    			if (iframe.src !== (iframe_src_value = "https://www.entitykb.org/")) attr_dev(iframe, "src", iframe_src_value);
    			attr_dev(iframe, "class", "svelte-jbahxs");
    			add_location(iframe, file$7, 41, 8, 983);
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
    		source: "(41:34) ",
    		ctx
    	});

    	return block;
    }

    // (39:33) 
    function create_if_block_2(ctx) {
    	let iframe;
    	let iframe_src_value;

    	const block = {
    		c: function create() {
    			iframe = element("iframe");
    			attr_dev(iframe, "title", "Swagger API");
    			if (iframe.src !== (iframe_src_value = "/docs")) attr_dev(iframe, "src", iframe_src_value);
    			attr_dev(iframe, "class", "svelte-jbahxs");
    			add_location(iframe, file$7, 39, 8, 890);
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
    		source: "(39:33) ",
    		ctx
    	});

    	return block;
    }

    // (35:36) 
    function create_if_block_1$1(ctx) {
    	let div;
    	let detailview;
    	let current;

    	detailview = new DetailView({
    			props: { key: /*selectKey*/ ctx[1] },
    			$$inline: true
    		});

    	const block = {
    		c: function create() {
    			div = element("div");
    			create_component(detailview.$$.fragment);
    			attr_dev(div, "id", "content");
    			attr_dev(div, "class", "svelte-jbahxs");
    			add_location(div, file$7, 35, 4, 779);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			mount_component(detailview, div, null);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			const detailview_changes = {};
    			if (dirty & /*selectKey*/ 2) detailview_changes.key = /*selectKey*/ ctx[1];
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
    		id: create_if_block_1$1.name,
    		type: "if",
    		source: "(35:36) ",
    		ctx
    	});

    	return block;
    }

    // (31:4) {#if (choice === "admin")}
    function create_if_block$4(ctx) {
    	let div;
    	let listview;
    	let updating_selectKey;
    	let current;

    	function listview_selectKey_binding(value) {
    		/*listview_selectKey_binding*/ ctx[3].call(null, value);
    	}

    	let listview_props = {};

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
    			add_location(div, file$7, 31, 4, 660);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			mount_component(listview, div, null);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			const listview_changes = {};

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
    		id: create_if_block$4.name,
    		type: "if",
    		source: "(31:4) {#if (choice === \\\"admin\\\")}",
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
    		/*menu_choice_binding*/ ctx[2].call(null, value);
    	}

    	let menu_props = {};

    	if (/*choice*/ ctx[0] !== void 0) {
    		menu_props.choice = /*choice*/ ctx[0];
    	}

    	menu = new Menu({ props: menu_props, $$inline: true });
    	binding_callbacks.push(() => bind(menu, "choice", menu_choice_binding));
    	const if_block_creators = [create_if_block$4, create_if_block_1$1, create_if_block_2, create_if_block_3];
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
    			add_location(main, file$7, 27, 0, 583);
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

    	$$self.$capture_state = () => ({
    		Menu,
    		Bottom,
    		ListView,
    		DetailView,
    		choice,
    		selectKey,
    		updateKey,
    		updateChoice
    	});

    	$$self.$inject_state = $$props => {
    		if ("choice" in $$props) $$invalidate(0, choice = $$props.choice);
    		if ("selectKey" in $$props) $$invalidate(1, selectKey = $$props.selectKey);
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

    	return [choice, selectKey, menu_choice_binding, listview_selectKey_binding];
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
