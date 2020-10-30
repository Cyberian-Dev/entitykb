
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
    function element(name) {
        return document.createElement(name);
    }
    function text(data) {
        return document.createTextNode(data);
    }
    function space() {
        return text(' ');
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

    /* src/Admin.svelte generated by Svelte v3.24.1 */

    const file$2 = "src/Admin.svelte";

    function create_fragment$2(ctx) {
    	let table;
    	let thead;
    	let tr0;
    	let th0;
    	let t0;
    	let th1;
    	let t2;
    	let th2;
    	let t4;
    	let th3;
    	let t6;
    	let th4;
    	let t8;
    	let th5;
    	let t10;
    	let tbody;
    	let tr1;
    	let td0;
    	let div;
    	let i;
    	let t11;
    	let t12;
    	let td1;
    	let t14;
    	let td2;
    	let t16;
    	let td3;
    	let t18;
    	let td4;
    	let t19;
    	let td5;

    	const block = {
    		c: function create() {
    			table = element("table");
    			thead = element("thead");
    			tr0 = element("tr");
    			th0 = element("th");
    			t0 = space();
    			th1 = element("th");
    			th1.textContent = "Key";
    			t2 = space();
    			th2 = element("th");
    			th2.textContent = "Label";
    			t4 = space();
    			th3 = element("th");
    			th3.textContent = "Name";
    			t6 = space();
    			th4 = element("th");
    			th4.textContent = "Synonyms";
    			t8 = space();
    			th5 = element("th");
    			th5.textContent = "Attributes";
    			t10 = space();
    			tbody = element("tbody");
    			tr1 = element("tr");
    			td0 = element("td");
    			div = element("div");
    			i = element("i");
    			t11 = text(" Add Node");
    			t12 = space();
    			td1 = element("td");
    			td1.textContent = "US|COUNTRY";
    			t14 = space();
    			td2 = element("td");
    			td2.textContent = "COUNTRY";
    			t16 = space();
    			td3 = element("td");
    			td3.textContent = "United States";
    			t18 = space();
    			td4 = element("td");
    			t19 = space();
    			td5 = element("td");
    			add_location(th0, file$2, 3, 6, 95);
    			add_location(th1, file$2, 4, 6, 111);
    			add_location(th2, file$2, 5, 6, 130);
    			add_location(th3, file$2, 6, 6, 151);
    			add_location(th4, file$2, 7, 6, 171);
    			add_location(th5, file$2, 8, 6, 195);
    			add_location(tr0, file$2, 2, 4, 84);
    			attr_dev(thead, "class", "full-width");
    			add_location(thead, file$2, 1, 2, 53);
    			attr_dev(i, "class", "plus icon");
    			add_location(i, file$2, 15, 10, 354);
    			attr_dev(div, "class", "ui small primary labeled icon button");
    			add_location(div, file$2, 14, 8, 293);
    			attr_dev(td0, "class", "collapsing");
    			add_location(td0, file$2, 13, 6, 261);
    			add_location(td1, file$2, 18, 6, 422);
    			add_location(td2, file$2, 19, 6, 448);
    			add_location(td3, file$2, 20, 6, 471);
    			add_location(td4, file$2, 21, 6, 500);
    			add_location(td5, file$2, 22, 6, 516);
    			add_location(tr1, file$2, 12, 4, 250);
    			add_location(tbody, file$2, 11, 2, 238);
    			attr_dev(table, "class", "ui compact celled definition table");
    			add_location(table, file$2, 0, 0, 0);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, table, anchor);
    			append_dev(table, thead);
    			append_dev(thead, tr0);
    			append_dev(tr0, th0);
    			append_dev(tr0, t0);
    			append_dev(tr0, th1);
    			append_dev(tr0, t2);
    			append_dev(tr0, th2);
    			append_dev(tr0, t4);
    			append_dev(tr0, th3);
    			append_dev(tr0, t6);
    			append_dev(tr0, th4);
    			append_dev(tr0, t8);
    			append_dev(tr0, th5);
    			append_dev(table, t10);
    			append_dev(table, tbody);
    			append_dev(tbody, tr1);
    			append_dev(tr1, td0);
    			append_dev(td0, div);
    			append_dev(div, i);
    			append_dev(div, t11);
    			append_dev(tr1, t12);
    			append_dev(tr1, td1);
    			append_dev(tr1, t14);
    			append_dev(tr1, td2);
    			append_dev(tr1, t16);
    			append_dev(tr1, td3);
    			append_dev(tr1, t18);
    			append_dev(tr1, td4);
    			append_dev(tr1, t19);
    			append_dev(tr1, td5);
    		},
    		p: noop,
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(table);
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

    function instance$2($$self, $$props) {
    	const writable_props = [];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<Admin> was created with unknown prop '${key}'`);
    	});

    	let { $$slots = {}, $$scope } = $$props;
    	validate_slots("Admin", $$slots, []);
    	return [];
    }

    class Admin extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$2, create_fragment$2, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "Admin",
    			options,
    			id: create_fragment$2.name
    		});
    	}
    }

    /* src/App.svelte generated by Svelte v3.24.1 */
    const file$3 = "src/App.svelte";

    // (20:34) 
    function create_if_block_3(ctx) {
    	let iframe;
    	let iframe_src_value;

    	const block = {
    		c: function create() {
    			iframe = element("iframe");
    			if (iframe.src !== (iframe_src_value = "https://www.entitykb.org/")) attr_dev(iframe, "src", iframe_src_value);
    			attr_dev(iframe, "class", "svelte-1mlijc1");
    			add_location(iframe, file$3, 20, 8, 500);
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
    		id: create_if_block_3.name,
    		type: "if",
    		source: "(20:34) ",
    		ctx
    	});

    	return block;
    }

    // (18:34) 
    function create_if_block_2(ctx) {
    	let iframe;
    	let iframe_src_value;

    	const block = {
    		c: function create() {
    			iframe = element("iframe");
    			if (iframe.src !== (iframe_src_value = "https://www.entitykb.org/")) attr_dev(iframe, "src", iframe_src_value);
    			attr_dev(iframe, "class", "svelte-1mlijc1");
    			add_location(iframe, file$3, 18, 8, 407);
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
    		id: create_if_block_2.name,
    		type: "if",
    		source: "(18:34) ",
    		ctx
    	});

    	return block;
    }

    // (16:33) 
    function create_if_block_1(ctx) {
    	let iframe;
    	let iframe_src_value;

    	const block = {
    		c: function create() {
    			iframe = element("iframe");
    			if (iframe.src !== (iframe_src_value = "/docs")) attr_dev(iframe, "src", iframe_src_value);
    			attr_dev(iframe, "class", "svelte-1mlijc1");
    			add_location(iframe, file$3, 16, 8, 334);
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
    		id: create_if_block_1.name,
    		type: "if",
    		source: "(16:33) ",
    		ctx
    	});

    	return block;
    }

    // (12:4) {#if (choice === "admin")}
    function create_if_block(ctx) {
    	let div;
    	let admin;
    	let current;
    	admin = new Admin({ $$inline: true });

    	const block = {
    		c: function create() {
    			div = element("div");
    			create_component(admin.$$.fragment);
    			attr_dev(div, "id", "content");
    			attr_dev(div, "class", "svelte-1mlijc1");
    			add_location(div, file$3, 12, 4, 244);
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
    		id: create_if_block.name,
    		type: "if",
    		source: "(12:4) {#if (choice === \\\"admin\\\")}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$3(ctx) {
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
    	const if_block_creators = [create_if_block, create_if_block_1, create_if_block_2, create_if_block_3];
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
    			add_location(main, file$3, 8, 0, 167);
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
    		id: create_fragment$3.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$3($$self, $$props, $$invalidate) {
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
    		init(this, options, instance$3, create_fragment$3, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "App",
    			options,
    			id: create_fragment$3.name
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
