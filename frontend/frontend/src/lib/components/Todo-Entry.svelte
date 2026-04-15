<script>
    let { id, name, description, ondelete, onupdate } = $props();
    let editing = $state(false);
    let editName = $state('');
    let editDesc = $state('');

    function startEdit() {
        editName = name;
        editDesc = description;
        editing = true;
    }

    function save() {
        onupdate(id, { name: editName, description: editDesc });
        editing = false;
    }
</script>

<div class="entry">
    {#if editing}
        <input bind:value={editName} />
        <input bind:value={editDesc} />
        <button onclick={save}>Save</button>
        <button onclick={() => editing = false}>Cancel</button>
    {:else}
        <strong>{name}</strong> - {description}
        <button onclick={startEdit}>Edit</button>
        <button onclick={() => ondelete(id)}>Delete</button>
    {/if}
</div>

<style>
    .entry {
        display: flex;
        gap: 8px;
        align-items: center;
        padding: 4px 0;
    }
    input {
        padding: 2px 4px;
    }
</style>
