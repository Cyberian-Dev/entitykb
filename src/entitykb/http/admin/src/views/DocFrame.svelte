<script>
    export let source = null;
    export let title = null;
    $: document.title = title;
</script>

<iframe title={title} src={source}></iframe>

<style>
    iframe {
        width: 100%;
        height: calc(85vh);
        border: 0;
    }
</style>

