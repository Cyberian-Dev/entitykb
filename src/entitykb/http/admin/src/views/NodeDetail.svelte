<script>
    import {onMount} from 'svelte';
    import {push, pop} from "svelte-spa-router";
    import {toastFail} from "../common/toast";

    import {manager} from '../kb/manager';
    import {Schema} from "../kb/schema";
    import ColumnFilter from "../common/ColumnFilter.svelte"
    import Pagination from "../common/Pagination.svelte"

    export let params = {};
    let schema = Schema.instance();
    let entity = null;
    let neighbors = [];
    let isDynamic = false;

    let labelOptions = [];
    let verbOptions = [];
    const directions = ["Incoming", "Outgoing"];

    const nextRequest = {
        key: '',
        direction: '',
        verb: '',
        name: '',
        label: '',
        page: 0,
    };

    const loadEntity = async () => {
        entity = await manager.getNode(params.key);
        if (!entity) {
            entity = await manager.findOne(params.key);
            isDynamic = true;
        }

        if (entity) {
            nextRequest["key"] = entity.key;
            await loadNeighbors();
            document.title = `Detail: ${entity.name} [${entity.label}]`;
        } else {
            toastFail(`Failed to load: ${params.key}`);
            await push("/");
        }
    };

    const loadNeighbors = async () => {
        neighbors = null;
        if (nextRequest.key) {
            neighbors = await manager.getNeighbors(nextRequest);
        }
    };

    const onUpdate = async (event) => {
        nextRequest[event.detail.name] = event.detail.value;
        nextRequest["page"] = 0;
        await loadNeighbors();
    };

    async function doPageChange(event) {
        nextRequest["page"] = event.detail;
        await loadNeighbors();
    }

    const openRow = (key) => {
        const encodedKey = encodeURIComponent(key);
        push("/detail/" + encodedKey);
        nextRequest["page"] = 0;
    };

    const openEdit = () => {
        push("/edit/" + entity.key);
    };

    $: loadEntity(params.key);
</script>

{#if entity && schema}
    <div class="ui stackable two column grid">
        <div class="six wide column">
            <h2>Node Details</h2>
            <table class="ui definition table top aligned">
                <tbody>
                <tr>
                    <td class="two wide column">name:</td>
                    <td class="five wide column">{entity.name}</td>
                </tr>
                <tr>
                    <td>label:</td>
                    <td>{entity.label}</td>
                </tr>
                <tr>
                    <td>key:</td>
                    <td>{entity.key}</td>
                </tr>
                {#each entity.attributes as [name, value]}
                    <tr>
                        <td>{name}:</td>
                        <td>
                            {#if value instanceof Array}
                                {#each value as item}
                                    {item}<br/>
                                {/each}
                            {:else if value instanceof Object}
                                <table class="ui compact celled table top aligned">
                                    {#each Object.entries(value) as kv}
                                        <tr>
                                            <td>{kv[0]}:</td>
                                            <td>{kv[1]}</td>
                                        </tr>
                                    {/each}
                                </table>
                            {:else if (value.startsWith("http://") || value.startsWith("https://"))}
                                <a target="_blank" href="{value}">{value}</a>
                            {:else}
                                {value}
                            {/if}
                        </td>
                    </tr>
                {/each}
                </tbody>
            </table>
<!--            {#if (!isDynamic)}-->
<!--                <div class="ui right floated blue button"-->
<!--                     on:click={openEdit}>-->
<!--                    <i class="edit icon"></i>-->
<!--                    Edit Node-->
<!--                </div>-->
<!--            {/if}-->
        </div>
        <div class="ten wide column">
            <div class="ui grid">
                <div class="row">
                    <div class="column">
                        <h2>Relationships</h2>
                    </div>
                    <div class="ten wide column"></div>
                    <div class="column">
                        {#if neighbors}
                        <Pagination page={nextRequest.page}
                                    page_count={neighbors.length}
                                    on:doPageChange={doPageChange}
                        />
                        {/if}
                    </div>
                </div>
            </div>

            <table class="ui striped selectable celled table top aligned">
                <thead class="full-width">
                <tr>
                    <th class="two wide" nowrap="nowrap">
                        <ColumnFilter name="direction"
                                      display="Direction"
                                      options={directions}
                                      on:update={onUpdate}/>
                    </th>
                    <th class="two wide" nowrap="nowrap">
                        <ColumnFilter name="verb" display="Verb"
                                      options={schema.verbs}
                                      on:update={onUpdate}/>
                    </th>
                    <th class="three wide" nowrap="nowrap">
                        <ColumnFilter name="name" display="Name"
                                      on:update={onUpdate}/>
                    </th>
                    <th class="two wide">
                        <ColumnFilter name="label" display="Label"
                                      options={schema.labels}
                                      on:update={onUpdate}/>
                    </th>
                </tr>
                </thead>
            <tbody>
                {#if !neighbors}
                <tr>
                    <td class="no-rels" colspan="4">
                        {#if neighbors === null}
                            Loading....
                        {:else if neighbors === false}
                            Load failed.
                        {:else}
                            No relationships found.
                        {/if}
                    </td>
                </tr>
                {:else}
                    {#each neighbors as neighbor}
                    <tr on:click={openRow(neighbor.key)}>
                        <td>{neighbor.direction}</td>
                        <td>{neighbor.verb}</td>
                        <td>{neighbor.name}</td>
                        <td>{neighbor.label}</td>
                    </tr>
                    {/each}
                {/if}
            </table>
        </div>
    </div>
{/if}

<style>
    h2 {
        min-height: 2em;
    }

    .no-rels {
        text-align: center !important;
        font-style: italic;
    }
</style>
