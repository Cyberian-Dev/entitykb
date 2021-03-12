<script>
    export let label;
    export let value = [];
    let editPosition = null;
    let removePosition = null;

    const onClickItem = (event) => {
        editPosition = parseInt(event.target.dataset.position);
    };

    const onDelete = (event) => {
        removePosition = parseInt(event.target.parentNode.dataset.position);

        window.$("#remove-item").modal({
            onApprove: function () {
                value = value.filter((_, index) => index !== removePosition);
            }
        }).modal('show');
    };

    const onAdd = () => {
        value = [...value, ""];
        editPosition = value.length - 1;
    };

    const clearEdit = () => {
        if (editPosition === (value.length - 1)) {
            if (!value[editPosition]) {
                value = value.filter((_, index) => index !== editPosition);
            }
        }
        editPosition = null;
    };

    const saveEdit = (event) => {
        if (event.target.value) {
            value[editPosition] = event.target.value;
        } else {
            value = value.filter((_, index) => index !== editPosition);
        }
        editPosition = null;
    };

    const handleKey = (event) => {
        if (event.code === "Escape") {
            clearEdit();

        } else if (event.code === "Enter") {
            event.preventDefault();
            saveEdit(event);
            return false;
        }
    };
</script>


<div class="field">
    <div class="ui labeled right input">
        <div class="ui label">
            {label}:
        </div>
        <div class="array">
            {#each (value || []) as item, position}
                <div class="item">
                    {#if position === editPosition}
                        <div class="edit">
                            <input on:keydown={handleKey}
                                   on:blur={saveEdit}
                                   data-position={position}
                                   value={item}
                                   autofocus/>
                        </div>
                    {:else}
                        <div class="view"
                             on:click={onClickItem}
                             data-position={position}>
                            {item}
                            <i on:click={onDelete} class="trash icon"></i>
                        </div>
                    {/if}
                </div>
            {/each}
            <div class="item">
                <div on:click={onAdd} class="add">
                    Add another item
                    <i class="circle plus icon"></i>
                </div>
            </div>
        </div>
    </div>
</div>

<div id="remove-item" class="ui tiny modal">
    <div class="header">{value[removePosition]}</div>
    <div class="content">
        <p>
            Are you should you want to remove?<br/>
        </p>
    </div>
    <div class="actions">
        <div class="ui approve positive button">Yes, remove.</div>
        <div class="ui cancel negative button">Cancel, keep.</div>
    </div>
</div>


<style>
    .ui.label {
        width: 8em;
        text-align: left;
    }

    .array {
        padding-top: .2em;
        padding-left: 0.5em;
        min-width: 25.8em;
    }

    div.item {
        width: 100%;
        text-align: left;
    }

    /** view **/

    div.view {
        padding: .5em;
    }

    div.view:hover {
        background-color: #FFFFAA;
        cursor: pointer;
    }

    .trash.icon {
        color: #DDCCCC;
        float: right;
        padding-left: 1em;
        padding-right: 1em;
    }

    .trash.icon:hover {
        color: red;
        font-weight: bold;
    }

    /** edit **/

    div.edit input {
        width: 100% !important;
        padding: .45em !important;
    }


    /** add item **/

    div.add {
        color: #AAAAAA;
        padding: .5em;
        font-style: italic;
    }

    div.add:hover {
        background-color: #CCEEDD;
        cursor: pointer;
        color: #333333;
    }

    .plus.icon {
        color: #99CC99;
        float: right;
        padding-left: 1em;
        padding-right: 1em;
    }

    .plus.icon:hover {
        color: #66FF66;
        font-weight: bold;
    }
</style>