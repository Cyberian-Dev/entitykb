<script>
    import {search} from './api.js';
    import Pagination from "./Pagination.svelte";

    let term = '';
    let key = '';
    let label = '';
    let attr_name = '';
    let attr_value = '';
    let page = 0;
    let showFilter = false;

    let data = {"nodes": [], "trails": []};
    const hide_attrs = ["key", "label", "name", "synonyms"];

    const onChange = async () => {
        page = 0;
        data = await search(term, key, label, attr_name, attr_value, page);
    };

    const onChangePage = async () => {
        data = await search(term, key, label, attr_name, attr_value, page);
    };

    const showFilters = () => {
        showFilter = true;
    };

    const clearFilters = () => {
        term = '';
        key = '';
        label = '';
        attr_name = '';
        attr_value = '';
        page = 0;
        showFilter = false;
    };

    $: onChange(term);
    $: onChange(key);
    $: onChange(label);
    $: onChange(attr_name);
    $: onChange(attr_value);
    $: onChangePage(page);
</script>

<div class="ui grid">
    <div class="eight wide column">
        {#if showFilter}
        <button class="ui labeled icon red button" on:click={clearFilters}>
          <i class="minus circle icon"></i>
          Clear Filters
        </button>
        {:else}
        <button class="ui labeled icon blue button" on:click={showFilters}>
            <i class="filter icon"></i>
            Show Filters
        </button>
        {/if}
    </div>
    <div class="eight wide column right aligned">
       <Pagination bind:page={page}/>
    </div>
</div>

<table class="ui compact celled striped table top aligned">
    <thead class="full-width">
    <tr>
        <th class="two wide">
            Name (Synonyms)
        </th>
        <th class="two wide">
            Key
        </th>
        <th class="two wide">
            Label
        </th>
        <th class="four wide">
            Attributes
        </th>
    </tr>
    {#if showFilter}
    <tr class="center aligned">
        <th><input placeholder="prefix" bind:value={term}></th>
        <th><input placeholder="key" bind:value={key}></th>
        <th><input placeholder="label" bind:value={label}></th>
        <th nowrap="nowrap">
            <input placeholder="name" bind:value={attr_name}>
            &thickapprox;
            <input placeholder="value" bind:value={attr_value}>
        </th>
    </tr>
    {/if}
    </thead>
    <tbody>
    {#each data.nodes as node}
        <tr>
            <td>
                {node.name}
                {#if node.synonyms}
                    {#each node.synonyms as synonym}
                        {synonym}
                    {/each}
                {/if}
            </td>
            <td>{node.key}</td>
            <td>{node.label}</td>
            <td>
                <table class="ui compact celled table top aligned">
                    {#each Object.keys(node) as name}
                        {#if (node[name] != null) && !hide_attrs.includes(name)}
                            <tr class="top aligned">
                                <td class="four wide field_name">{name}:</td>
                                <td class="twelve wide">{node[name]}</td>
                            </tr>
                        {/if}
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