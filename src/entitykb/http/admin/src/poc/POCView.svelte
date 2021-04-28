<script>
    import Textarea from "../common/Textarea.svelte";
    import {manager} from '../kb/manager';

    let doc = {text: '', spans: [], tokens: []};
    let text = "";
    let render = "";
    let isLoading = false;

    const doParse = async () => {
        isLoading = true;
        doc = await manager.parseDoc({text: text, labels: []});
        console.log(doc);
        isLoading = false;

        render = "";
        let inLine = false;
        let firstOffsets = new Map();
        let lastOffsets = new Map();

        doc.spans.forEach(span => {
            firstOffsets.set(span.tokens[0].offset, span);
            lastOffsets.set(span.tokens[span.tokens.length - 1].offset, span);
        });

        console.log(firstOffsets);
        console.log(lastOffsets);

        doc.tokens.forEach(token => {
            if (token.token === "\n") {
                render += "<br/><br/>";
                inLine = false;

            } else {
                if (inLine) {
                    render += " ";
                } else {
                    inLine = true;
                }
                let span = firstOffsets.get(token.offset);
                if (span) {
                    let label = span.entity.label;
                    if (label === "CUI") {
                        label = Object.values(span.entity.semantic_map)[0][0];
                    }

                    render += `<mark data-entity="${label}" data-tooltip="${span.entity.name} [${label}]">`;
                }

                render += token.token;

                if (lastOffsets.get(token.offset)) {
                    render += "</mark>"
                }
            }
        });

        // window.$('mark').popup();
    };
</script>

<main>
    <div class="entities">
        {@html render}
    </div>

    <div id="form">
        <Textarea bind:value={text}/>
        <br/>
        <button class:loading={isLoading} on:click={doParse}
                class="ui right aligned primary button">
            Parse
        </button>
    </div>
</main>

<style>
    main {
        text-align: left;
        padding: 1em;
        max-width: 800px;
        margin: 0 auto;
    }

    div.entities {
        font-size: 1.4em;
        padding-bottom: 2em;
        line-height: 1.7;
    }

    [data-entity]:before {
      content: attr(data-entity);
    }
</style>
