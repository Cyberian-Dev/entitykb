<script>
    import {createEventDispatcher} from 'svelte';
    import {loginUser} from "./manager";

    const dispatch = createEventDispatcher();

    let hasError = false;

    const onSubmit = async (e) => {
        const success = await loginUser(
                e.target.elements['username'].value,
                e.target.elements['password'].value,
        );
        hasError = !success;
    };
</script>

<h2>Login</h2>

<form on:submit|preventDefault={onSubmit} class="ui large form">
    <div class="field">
        <div class="ui left icon input">
            <i class="user icon"></i>
            <input required="required" type="text" name="username"
                   placeholder="Username">
        </div>
    </div>
    <div class="field">
        <div class="ui left icon input">
            <i class="lock icon"></i>
            <input required="required" type="password" name="password"
                   placeholder="Password">
        </div>
    </div>

    <div>
        <button class="ui large primary submit button"
                type="submit">
            Submit
        </button>
    </div>
    {#if hasError }
        <div class="ui visible error message">
            Invalid Username or Password
        </div>
    {:else}
        <div>&nbsp;</div>
    {/if}
</form>

<style>
    h2 {
        padding-bottom: 1em;
    }
</style>
