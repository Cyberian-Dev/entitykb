<script>
    import {push} from "svelte-spa-router";

    import MultiSelect from "../common/MultiSelect.svelte"
    import {manager} from '../kb/manager';
    import {Schema} from "../kb/schema";

    let schema = Schema.instance();
    let doc = {text: '', spans: [], tokens: []};
    const nextRequest = {
        text: '',
        labels: [],
    };

    const onUpdate = async (event) => {
        nextRequest[event.detail.name] = event.detail.value;
    };

    const doParse = async () => {
        doc = await manager.parseDoc(nextRequest);
    };

    const openRow = (entity) => {
        push("/detail/" + entity.key);
    };

    document.title = "Parse Text";
</script>

<div class="ui stackable sixteen column grid">
    <div class="six wide column">
        <h2>Parse</h2>
        <div class="ui form horizontally">
            <div class="field">
                <label>Text:</label>
                <textarea bind:value={nextRequest.text} rows="15"></textarea>
            </div>
            <div class="field">
                <label>Labels:</label>
                <MultiSelect
                        display="Labels"
                        name="labels"
                        options={schema.labels}
                        on:update={onUpdate}
                />
            </div>
            <div class="field">
                <button on:click={doParse} class="positive ui button">
                    Parse
                </button>
            </div>
        </div>
    </div>
    <div class="ten wide column">
        <h2>Entities</h2>

        <div class="ui horizontally padded">
            <table class="ui compact selectable celled striped table top aligned">
                <thead class="full-width">
                <tr>
                    <th class="four wide">Name</th>
                    <th class="four wide">Label</th>
                    <th class="four wide">Key</th>
                    <th class="four wide">Tokens</th>
                </tr>
                </thead>
                <tbody>
                {#if doc === null}
                    <tr><td colspan="4">Failed to Parse.</td></tr>
                {:else}
                    {#each doc.spans as span}
                        <tr on:click={openRow(span.entity)}>
                            <td>{span.entity.name}</td>
                            <td>{span.entity.label}</td>
                            <td>{span.entity.key}</td>
                            <td>
                                <table class="ui compact celled table top aligned">
                                    {#each span.tokens as token}
                                        <tr>
                                            <td class="token_offset four wide">{token.offset}</td>
                                            <td class="twelve wide">{token.token}</td>
                                        </tr>
                                    {/each}
                                </table>
                            </td>
                        </tr>
                    {/each}
                {/if}
                </tbody>
            </table>
        </div>
    </div>
</div>
