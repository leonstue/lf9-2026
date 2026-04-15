<script>
    import TodoEntry from "$lib/components/Todo-Entry.svelte";
    import { onMount } from "svelte";
    import { page } from "$app/state";

    const API = "http://127.0.0.1:5000";
    let entries = $state([]);
    let newName = $state("");
    let newDesc = $state("");

    const listId = $derived(page.params.list_id);

    onMount(() => {
        loadEntries();
    });

    async function loadEntries() {
        const res = await fetch(`${API}/todo-list/${listId}`);
        if (res.ok) entries = await res.json();
    }

    async function addEntry() {
        if (!newName.trim() || !newDesc.trim()) return;
        await fetch(`${API}/todo-list/${listId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: newName, description: newDesc })
        });
        newName = "";
        newDesc = "";
        await loadEntries();
    }

    async function deleteEntry(id) {
        await fetch(`${API}/todo-list/entry/${id}`, { method: "DELETE" });
        await loadEntries();
    }

    async function updateEntry(id, body) {
        await fetch(`${API}/todo-list/entry/${id}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });
        await loadEntries();
    }
</script>

<a href="/">Back to lists</a>
<h1>Entries</h1>

<div class="entries">
    <input bind:value={newName} placeholder="Name" />
    <input bind:value={newDesc} placeholder="Description" />
    <button onclick={addEntry}>Add</button>
</div>

{#each entries as entry}
    <TodoEntry
        id={entry.id}
        name={entry.name}
        description={entry.description}
        ondelete={deleteEntry}
        onupdate={updateEntry}
    />
{/each}

<style>
    .entries {
        display: flex;
        gap: 8px;
        margin-bottom: 16px;
    }
</style>
