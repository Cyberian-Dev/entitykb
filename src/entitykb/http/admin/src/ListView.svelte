<script>
    import {search} from './api.js';
    import Pagination from "./Pagination.svelte";
    import ColumnFilter from "./ColumnFilter.svelte";
    import AttributeFilter from "./AttributeFilter.svelte";

    export let selectKey = null;
    let filters = {
        "name": '',
        "key": '',
        "label": '',
    };

    let page = 0;
    let data = {"nodes": [], "trails": []};

    const isAttribute = (fieldName) => {
        return !["key", "name", "label"].includes(fieldName);
    };

    const onUpdate = async (event) => {
        if (isAttribute(event.detail.name)) {
            filters = {
                "name": filters["name"],
                "key": filters["key"],
                "label": filters["label"],
            };

            if (event.detail.name && event.detail.value) {
                filters[event.detail.name] = event.detail.value;
            }

        } else {
            filters[event.detail.name] = event.detail.value;
        }

        page = 0;
    };

    const onRefresh = async () => {
        console.log(page);
        console.log(filters);

        data = await search(page, filters);
        console.log(data);
    };

    const openRow = (key) => {
        selectKey = key;
    };

    const iterateAttrs = (node) => {
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

    $: onRefresh(page, filters);
</script>

<div class="ui grid">
    <div class="eight wide column">
    </div>
    <div class="eight wide column right aligned">
        <Pagination bind:page={page}/>
    </div>
</div>

<table class="ui compact selectable celled striped table top aligned">
    <thead class="full-width">
    <tr>
        <th class="two wide">
            <ColumnFilter name="name" display="Name" on:update={onUpdate} />
        </th>
        <th class="two wide">
            <ColumnFilter name="key" display="Key" on:update={onUpdate} />
        </th>
        <th class="two wide">
            <ColumnFilter name="label" display="Label" on:update={onUpdate} />
        </th>
        <th class="four wide">
            <AttributeFilter on:update={onUpdate} />
        </th>
    </tr>
    </thead>
    <tbody>
    {#each data.nodes as node}
        <tr on:click={openRow(node.key)}>
            <td>{node.name}</td>
            <td>{node.key}</td>
            <td>{node.label}</td>
            <td>
                <table class="ui compact celled table top aligned">
                    {#each iterateAttrs(node) as kv}
                        <tr class="top aligned">
                            <td class="four wide field_name">{kv[0]}:</td>
                            <td class="twelve wide">{kv[1]}</td>
                        </tr>
                    {/each}
                </table>
            </td>
        </tr>
    {/each}
    </tbody>
</table>

<style>
    .field_name {
        font-weight: bold;
        color: #444444;
        background-color: #DDD5DD;
    }
</style>