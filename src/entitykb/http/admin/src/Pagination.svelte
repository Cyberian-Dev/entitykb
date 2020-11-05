<script>
    export let page = 0;
    let items = [];
    let addedNull = false;

    function onClick(evt) {
        page = parseInt(evt.target.attributes['data-value'].value);
    }

    function changePage() {
        items = [];
        let addedNull = false;
        for (let i=0; i <= page; i++) {
            if (i < 4) {
                items.push(i);
            } else if ((page - i) < 4) {
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

    $: changePage(page);
</script>

<b>Page:</b>

<div class="ui pagination tiny menu">
    {#each items as item}
        {#if item === null}
            <a class="disabled item">...</a>
        {:else}
        <a class="item"
           data-value={item}
           class:active={item === page}
           on:click={onClick}>
            {item + 1}
        </a>
        {/if}
    {/each}
</div>

<style>
    .menu .item {
        width: 2em;
    }
</style>