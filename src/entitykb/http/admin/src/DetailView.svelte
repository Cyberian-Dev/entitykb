<script>
    import {getNode, getEdges} from './api.js';
    import Pagination from "./Pagination.svelte";

    export let key = null;

    let node = {};
    let edges = [];
    let page = 0;
    let relationships = new Map();

    function addTrail(trail) {
        let neighbor = relationships.get(trail.end);

        function addEdge(edge) {
            const dir = edge.end === trail.end ? "outgoing" : "incoming";
            edges = [...edges,
                {
                    direction: dir,
                    verb: edge.verb,
                    key: neighbor.key,
                    label: neighbor.label,
                    name: neighbor.name,
                }
            ];
        }

        trail && trail.hops && trail.hops[0].edges.forEach(addEdge);
    }

    const onChange = async () => {
        node = await getNode(key);
        edges = [];

        let result = await getEdges(key, page);
        result.nodes.forEach(n => {
            relationships.set(n.key, n);
        });
        result.trails.forEach(addTrail);
        edges = edges;
    };

    const isAttribute = (fieldName) => {
        return !["key", "name", "label"].includes(fieldName);
    };

    const openRow = (rowKey) => {
        key = rowKey;
    };

    $: onChange(key, page);
</script>

<div class="ui grid">
    <div class="seven wide column">
        <h3>Node Details</h3>
        <table class="ui compact definition table">
            <tbody>
            <tr>
                <td class="two wide column">key</td>
                <td class="five wide column">{node['key']}</td>
            </tr>
            <tr>
                <td>name</td>
                <td>{node['name']}</td>
            </tr>
            <tr>
                <td>label</td>
                <td>{node['label']}</td>
            </tr>
            {#each Object.keys(node) as fieldName}
                {#if isAttribute(fieldName) && Boolean(node[fieldName])}
                    <tr>
                        <td>{fieldName}</td>
                        <td>{node[fieldName]}</td>
                    </tr>
                {/if}
            {/each}
            </tbody>
        </table>
    </div>
    <div class="nine wide column">
        <div class="ui grid">
            <div class="one wide column">
                <h3>Relationships</h3>
            </div>
            <div class="fifteen wide column right aligned">
                <Pagination bind:page={page}/>
            </div>
        </div>

        <table class="ui compact striped celled table">
            <thead class="full-width">
            <tr>
                <th class="one wide">Direction</th>
                <th class="one wide">Verb</th>
                <th class="four wide">Name</th>
                <th class="two wide">Label</th>
            </tr>
            </thead>
            <tbody>
            {#each edges as edge}
                <tr on:click={openRow(edge.key)}>
                    <td>{edge.direction}</td>
                    <td>{edge.verb}</td>
                    <td>{edge.name}</td>
                    <td>{edge.label}</td>
                </tr>
            {/each}
            </tbody>
        </table>
    </div>
</div>
