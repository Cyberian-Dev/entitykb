<script>
    import LoginForm from "./LoginForm.svelte";
</script>

<div id="authContainer" class="ui middle aligned center aligned grid">
    <div class="column">
        <h1 class="ui image header">
            <i class="lightbulb outline icon"></i> EntityKB
        </h1>
        <div id="authContent" class="ui top attached stacked segment">
            <LoginForm/>
        </div>
    </div>
</div>

<style>
    div#authContainer {
        height: calc(100vh);
        background-color: #e0e0e0;
    }

    div#authContent {
        padding-top: 1.5em;
        height: 30em;
    }

    .image {
        margin-top: -100px;
    }

    .image img {
        width: 2em !important;
    }

    .column {
        max-width: 450px;
    }
</style>