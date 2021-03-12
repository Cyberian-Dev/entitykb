<script>
    import {createEventDispatcher} from 'svelte';

    const dispatch = createEventDispatcher();

    export let waiting = false;
    export let error = "";
    let dirty = false;

    function submit(event) {
        dirty = false;
        dispatch("submit", {elements: event.target.elements});
    }

    function cancel() {
        dirty = false;
        dispatch("cancel");
    }

    function setDirty() {
        dirty = true;
    }
</script>


<div id="formContainer" class="ui aligned center aligned grid">
    <div class="column">
        <div class="ui top attached stacked segment">
            <h2>
                <slot name="heading"/>
            </h2>

            <form class="ui large form" id="formId"
                  on:submit|preventDefault={submit} on:change={setDirty}>

                <slot name="fields"/>

                <div id="buttons">
                    {#if waiting}
                        <button class="ui large primary disabled loading button">
                            Loading
                        </button>
                    {:else}
                        <button class="ui large primary button" type="submit">
                            Submit
                        </button>
                    {/if}
                    <span id="cancel">
                        <a href="javascript:void(0)"
                           on:click={cancel}>Cancel</a>
                    </span>
                </div>
            </form>
        </div>
        {#if !dirty && error}
            <div class="ui visible error message">
                {error}
            </div>
        {/if}
    </div>

    <!--
https://github.com/sveltejs/svelte/issues/4546#issuecomment-627357929
-->
    {#if false}
    <!--suppress CheckTagEmptyBody -->
        <slot></slot>
    {/if}
</div>

<style>
    h2 {
        padding-bottom: 1em;
    }

    div#buttons {
        padding-top: 2em;
    }

    .column {
        max-width: 600px !important;
    }

    div#formContainer {
        padding-top: 3em;
    }

    span#cancel a {
        color: #9999CC;
        margin-left: 3em;
    }
</style>
