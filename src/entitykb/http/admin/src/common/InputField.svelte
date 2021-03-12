<script>
    export let icon = "";
    export let label = "";
    export let placeholder = "";
    export let required = false;
    export let type = "text";
    export let value = "";
    export let readonly = false;

    placeholder = placeholder || label;

    const handleInputType = (e) => {
        e.target.type = type;
    };
</script>

<div class="field">
    <div class="ui labeled right icon input field">
        <div class:black={readonly} class="ui label">
            {label}:
        </div>
        {#if readonly}
            <span class="readonly">{value}</span>
        {:else}
        <input {required}
               {placeholder}
               on:input={handleInputType}
               bind:value/>
        {/if}
        {#if icon}<i class="{icon} icon"></i>{/if}
    </div>
</div>

<style>
    .ui.label {
        width: 8em;
        text-align: left;
    }
    .icon {
        width: 1.1em;
    }
    span.readonly {
        padding-top: .4em;
        padding-left: 1em;
        font-weight: bold;
        color: #666666;
    }
</style>