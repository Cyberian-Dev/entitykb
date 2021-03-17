<script>
    import {createEventDispatcher} from 'svelte';
    const dispatch = createEventDispatcher();

    export let page = 0;
    export let page_size = 10;
    export let page_count = 0;
    export let total_count = null;

    let page_min = 0;
    let page_max = 0;
    let has_prev = false;
    let has_next = false;

    const update_nums = () => {
        page_min = (page * page_size) + 1;
        page_max = (page * page_size) + page_count;
        has_prev = page > 0;
        has_next = page_max < total_count;
    };

    function firstPage() {
        dispatch("doPageChange", 0);
    }

    function previousPage() {
        dispatch("doPageChange", page - 1);
    }

    function nextPage() {
        dispatch("doPageChange", page + 1);
    }

    $: update_nums(page, page_size, page_count, total_count);
</script>
<div id="pagination">
    <button class="circular ui icon button"
            class:disabled={!has_prev}
            on:click={firstPage}>
        <i class="angle double left icon"></i>
    </button>

    <button class="circular ui icon button"
            class:disabled={!has_prev}
            on:click={previousPage}>
        <i class="angle left icon"></i>
    </button>

    &nbsp;

    {#if page_max}
        {page_min.toLocaleString()} - {page_max.toLocaleString()}
        {#if total_count !== null}
            of {total_count.toLocaleString()}
        {/if}
    {/if}

    &nbsp;

    <button class="circular ui icon button"
            class:disabled={!has_next}
            on:click={nextPage}>
        <i class="angle right icon"></i>
    </button>
</div>

<style>
    div#pagination {
        white-space: nowrap !important;
        font-weight: bold;
        color: #999999;
    }
</style>
