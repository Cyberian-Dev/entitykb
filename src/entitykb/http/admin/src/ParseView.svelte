<script>
    import {onMount} from 'svelte';
    import {RequestManager} from './kb/manager';

    export let selectKey;
    let text = '';
    let labels_str = '';
    let spans = [];
    let labels = [];
    let page = 0;

    const manager = new RequestManager();

    onMount(() => {
        refreshData();
        setInterval(refreshData, 10);
    });

    const openRow = (key) => {
        selectKey = key;
    };

    const refreshData = async () => {
        const nextRequest = {text: text, labels: labels};

        if (manager.isAvailable(page, nextRequest)) {
            let doc = await manager.getDoc(page, nextRequest);
            spans = Boolean(doc) ? doc.spans : [];
        }
    };

    const updateLabels = () => {
        labels = labels_str.replace(",", " ").replace("  ", " ").split(" ").map(function(item) {
            return item.trim().toUpperCase();
        }).filter(function (s) {
            return s.length > 0;
        });
    };

    $: updateLabels(labels_str);

</script>

<div class="ui grid">
    <div class="two wide column">

    </div>
    <div class="twelve wide column">
        <h3>Enter Text:</h3>

        <div class="ui form horizontally">
            <textarea bind:value={text} rows="15"></textarea>
        </div>

        <h3>Labels (space-separated):</h3>
        <div>
            <input bind:value={labels_str} />
            {#if labels.length > 0}
                <ul>
                {#each labels as label}
                    <li>{label}</li>
                {/each}
                </ul>
            {/if}
        </div>

        <br/>

        <h3>Parsed Entities:</h3>

        <div class="ui horizontally padded">
            <table class="ui compact selectable celled striped table top aligned">
                <thead class="full-width">
                <tr>
                    <th class="two wide">Name</th>
                    <th class="two wide">Label</th>
                    <th class="two wide">Key</th>
                    <th class="four wide">Tokens</th>
                </tr>
                </thead>
                <tbody>
                {#each spans as span}
                <tr on:click={openRow(span.entity.key)}>
                    <td>{span.entity.name}</td>
                    <td>{span.entity.label}</td>
                    <td>{span.entity.key}</td>
                    <td>
                        <table class="ui compact celled table top aligned">
                        {#each span.tokens as token}
                            <tr>
                                <td class="token_offset two wide column">{token.offset}</td>
                                <td class="two wide column">{token.token}</td>
                            </tr>
                        {/each}
                        </table>
                    </td>
                </tr>
                {/each}
                </tbody>
            </table>
        </div>
    </div>
    <div class="two wide column"></div>
</div>

<style>
    .token_offset {
        font-weight: bold;
        color: #444444;
        background-color: #DDD5DD;
    }
</style>