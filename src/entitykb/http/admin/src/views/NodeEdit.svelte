<script>
    import {onMount} from 'svelte';
    import {push, pop} from "svelte-spa-router";
    import {toastFail} from "../common/toast";

    import {RequestManager} from '../kb/manager';
    import {Edit} from "../kb/edit";
    import {Entity} from "../kb/nodes";
    import {Schema} from "../kb/schema";
    import FormTemplate from "../common/FormTemplate.svelte";
    import InputField from "../common/InputField.svelte";
    import ArrayField from "../common/ArrayField.svelte";
    import SelectField from "../common/SelectField.svelte";
    import {toastOnCondition, toastClear} from "../common/toast";

    export let params = {};
    const manager = new RequestManager();
    const schema = Schema.instance();
    let edit = null;
    let error = "";
    let waiting = false;

    onMount(async () => {
        let entity;
        if (params.key) {
            entity = await manager.getNode(params.key);

        } else {
            entity = new Entity({label: params.label, name: ""})
        }

        if (entity) {
            edit = entity ? new Edit(entity, schema) : null;
            document.title = edit.title;
        } else {
            toastFail(`Failed to load: ${params.key}`);
            await pop();
        }
    });

    const submit = async () => {
        waiting = true;
        const success = await manager.saveEntity(edit.entity);
        toastOnCondition(success, `Save ${edit.title}: ${edit.name}`);

        if (success) {
            await push("/detail/" + success.key);

        } else {
            error = "Save failed, please check logs";
            waiting = false;
        }
    };

    const cancel = async () => {
        toastClear();
        await push("/detail/" + edit.key);
    };
</script>

{#if edit}
    <FormTemplate error={error}
                  waiting={waiting}
                  on:cancel={cancel}
                  on:submit={submit}>
        <span slot="heading">{edit.title}</span>

        <div slot="fields">
            {#if edit.isNew}
                <SelectField
                        label="Label"
                        options={schema.labelOptions}
                        bind:value={edit.label}
                />
            {:else}
                <InputField
                        label="Label"
                        readonly=true
                        value={edit.label}
                />
            {/if}
            <InputField
                    label="Name"
                    readonly={!edit.isNew}
                    bind:value={edit.name}
            />
            {#each edit.attributes as attribute}
                {#if attribute.type === "array"}
                    <ArrayField
                            label={attribute.title}
                            bind:value={edit.data[attribute.name]}
                    />
                {:else if attribute.type === "string"}
                    <InputField
                            label={attribute.title}
                            bind:value={edit.data[attribute.name]}
                            required={attribute.required}
                    />
                {/if}
            {/each}
        </div>
    </FormTemplate>
{:else}
    <div class="ui active inverted dimmer">
        <div class="ui text loader">Loading</div>
    </div>
{/if}
