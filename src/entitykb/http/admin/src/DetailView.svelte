<script>
    import {getNode, getNeighbors} from './api.js';

    export let key = null;

    let node = {};
    let neighbors = [];
    let page = 0;
    let edges = new Map();

    function addTrail(trail) {
        let items = edges.get(trail.end);
        if (!items) {
            items = [];
            edges.set(trail.end, items);
        }

        function addEdge(edge) {
            let direction = edge.end === trail.end ? ">>>" : "<<<";
            items.push({verb: edge.verb, direction: direction});
        }

        trail && trail.hops && trail.hops[0].edges.forEach(addEdge);
    }

    const onChange = async () => {
        node = await getNode(key);
        let result = await getNeighbors(key, page);

        neighbors = (result && result.nodes) || [];
        edges = new Map();
        let trails = (result && result.trails) || [];
        trails.forEach(addTrail);
    };

    const isAttribute = (fieldName) => {
        return !["key", "name", "label"].includes(fieldName);
    };

    const openRow = (rowKey) => {
        key = rowKey;
    };

    $: onChange(key);
</script>

<div class="ui grid">
    <div class="eight wide column">
        <h3>Node Details</h3>
        <table class="ui compact definition table">
            <tbody>
            <tr>
                <td>key</td>
                <td>{node['key']}</td>
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
    <div class="eight wide column">
        <h3>Neighbors</h3>
        <table class="ui compact striped celled table">
            <thead class="full-width">
            <tr>
                <th class="two wide">Edges</th>
                <th class="two wide">Key</th>
                <th class="two wide">Label</th>
                <th class="four wide">Name</th>
            </tr>
            </thead>
            <tbody>
            {#each neighbors as neighbor}
                <tr on:click={openRow(neighbor.key)}>
                    <td>
                        <ul class="edges">
                            {#each edges.get(neighbor.key) as edge}
                                <li class="edge">
                                    {edge.verb} <b>{edge.direction}</b>
                                </li>
                            {/each}
                        </ul>
                    </td>
                    <td>{neighbor.key}</td>
                    <td>{neighbor.label}</td>
                    <td>{neighbor.name}</td>
                </tr>
            {/each}
            </tbody>
        </table>
    </div>
</div>

<style>
    ul.edges {
        list-style-type: none;
        margin: 0;
        padding: 0;
    }
</style>
