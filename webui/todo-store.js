import { createStore } from "/js/AlpineStore.js";
import { toastFrontendError, toastFrontendSuccess } from "/components/notifications/notification-store.js";

async function api(action, payload = {}) {
    const res = await fetch(`/api/plugins/todo_list/${action}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!data.ok) {
        throw new Error(data.message || "Request failed");
    }
    return data;
}

export const store = createStore("todoListStore", {
    // State
    tasks: [],
    projects: [],
    agentProfiles: [],
    stats: { total: 0, pending: 0, in_progress: 0, blocked: 0, completed: 0, cancelled: 0 },
    loading: false,

    // Filters
    filterProject: "",
    filterStatus: "",
    filterPriority: "",
    filterSearch: "",
    filterTag: "",

    // Form
    formOpen: false,
    formEditing: null,
    formTitle: "",
    formDescription: "",
    formStatus: "pending",
    formPriority: "medium",
    formProgress: 0,
    formProject: "",
    formAgentProfile: "",
    formStartDate: "",
    formDueDate: "",
    formTags: "",
    formBlockedBy: [],

    // Linking
    linkMode: false,
    currentChatId: null,

    init() {
        this.currentChatId = window.A0_CONTEXT_ID || null;
    },

    onOpen() {
        this.loadTasks();
        this.currentChatId = window.A0_CONTEXT_ID || null;
    },

    cleanup() {
        this.tasks = [];
        this.projects = [];
        this.agentProfiles = [];
        this.resetForm();
        this.linkMode = false;
    },

    async loadTasks() {
        this.loading = true;
        try {
            const filters = {};
            if (this.filterProject) filters.project = this.filterProject;
            if (this.filterStatus) filters.status = this.filterStatus;
            if (this.filterPriority) filters.priority = this.filterPriority;
            if (this.filterSearch) filters.search = this.filterSearch;
            if (this.filterTag) filters.tag = this.filterTag;

            const data = await api("get_tasks", filters);
            this.tasks = data.tasks || [];
            this.projects = data.projects || [];
            this.agentProfiles = data.agent_profiles || [];
            this.stats = data.stats || { total: 0, pending: 0, in_progress: 0, blocked: 0, completed: 0, cancelled: 0 };
        } catch (err) {
            toastFrontendError(err.message, "Todo List");
        } finally {
            this.loading = false;
        }
    },

    openCreate() {
        this.resetForm();
        this.formOpen = true;
        this.formEditing = null;
    },

    openEdit(task) {
        this.formOpen = true;
        this.formEditing = task.id;
        this.formTitle = task.title || "";
        this.formDescription = task.description || "";
        this.formStatus = task.status || "pending";
        this.formPriority = task.priority || "medium";
        this.formProgress = task.progress || 0;
        this.formProject = task.project || "";
        this.formAgentProfile = task.agent_profile || "";
        this.formStartDate = task.start_date || "";
        this.formDueDate = task.due_date || "";
        this.formTags = (task.tags || []).join(", ");
        this.formBlockedBy = task.blocked_by ? [...task.blocked_by] : [];
    },

    resetForm() {
        this.formOpen = false;
        this.formEditing = null;
        this.formTitle = "";
        this.formDescription = "";
        this.formStatus = "pending";
        this.formPriority = "medium";
        this.formProgress = 0;
        this.formProject = "";
        this.formAgentProfile = "";
        this.formStartDate = "";
        this.formDueDate = "";
        this.formTags = "";
        this.formBlockedBy = [];
    },

    async saveTask() {
        const title = this.formTitle.trim();
        if (!title) {
            toastFrontendError("Title is required", "Todo List");
            return;
        }
        const payload = {
            title,
            description: this.formDescription.trim(),
            status: this.formStatus,
            priority: this.formPriority,
            progress: parseInt(this.formProgress, 10) || 0,
            project: this.formProject.trim(),
            agent_profile: this.formAgentProfile.trim(),
            start_date: this.formStartDate || null,
            due_date: this.formDueDate || null,
            tags: this.formTags.split(",").map(t => t.trim()).filter(Boolean),
            blocked_by: this.formBlockedBy.length > 0 ? this.formBlockedBy : [],
        };
        try {
            if (this.formEditing) {
                payload.task_id = this.formEditing;
                await api("update_task", payload);
                toastFrontendSuccess("Task updated", "Todo List");
            } else {
                await api("create_task", payload);
                toastFrontendSuccess("Task created", "Todo List");
            }
            this.resetForm();
            await this.loadTasks();
        } catch (err) {
            toastFrontendError(err.message, "Todo List");
        }
    },

    async deleteTask(taskId) {
        if (!confirm("Delete this task?")) return;
        try {
            await api("delete_task", { task_id: taskId });
            toastFrontendSuccess("Task deleted", "Todo List");
            await this.loadTasks();
        } catch (err) {
            toastFrontendError(err.message, "Todo List");
        }
    },

    async toggleStatus(task) {
        const next = task.status === "completed" ? "pending" : "completed";
        try {
            await api("update_task", { task_id: task.id, status: next, progress: next === "completed" ? 100 : task.progress });
            await this.loadTasks();
        } catch (err) {
            toastFrontendError(err.message, "Todo List");
        }
    },

    async linkChat(taskId) {
        if (!this.currentChatId) {
            toastFrontendError("No active chat to link", "Todo List");
            return;
        }
        try {
            await api("link_chat", { task_id: taskId, chat_id: this.currentChatId, action: "link" });
            toastFrontendSuccess("Chat linked to task", "Todo List");
            await this.loadTasks();
        } catch (err) {
            toastFrontendError(err.message, "Todo List");
        }
    },

    async unlinkChat(taskId, chatId) {
        try {
            await api("link_chat", { task_id: taskId, chat_id: chatId, action: "unlink" });
            toastFrontendSuccess("Chat unlinked", "Todo List");
            await this.loadTasks();
        } catch (err) {
            toastFrontendError(err.message, "Todo List");
        }
    },

    addBlockedBy(taskId) {
        if (!this.formBlockedBy.includes(taskId)) {
            this.formBlockedBy = [...this.formBlockedBy, taskId];
        }
    },

    removeBlockedBy(taskId) {
        this.formBlockedBy = this.formBlockedBy.filter(id => id !== taskId);
    },

    isUnblocked(task) {
        if (!task.blocked_by || task.blocked_by.length === 0) return false;
        return task.blocked_by.every(bid => {
            const blocker = this.tasks.find(t => t.id === bid);
            return blocker && (blocker.status === "completed" || blocker.status === "cancelled");
        });
    },

    clearFilters() {
        this.filterProject = "";
        this.filterStatus = "";
        this.filterPriority = "";
        this.filterSearch = "";
        this.filterTag = "";
        this.loadTasks();
    },

    statusClass(status) {
        const map = {
            pending: "bg-gray-500/20 text-gray-300",
            in_progress: "bg-blue-500/20 text-blue-300",
            blocked: "bg-red-500/20 text-red-300",
            completed: "bg-green-500/20 text-green-300",
            cancelled: "bg-yellow-500/20 text-yellow-300",
        };
        return map[status] || map.pending;
    },

    statusLabel(status) {
        const map = {
            pending: "Pending",
            in_progress: "In Progress",
            blocked: "Blocked",
            completed: "Done",
            cancelled: "Cancelled",
        };
        return map[status] || status;
    },

    priorityClass(priority) {
        const map = {
            low: "text-gray-400",
            medium: "text-blue-400",
            high: "text-orange-400",
            urgent: "text-red-400",
        };
        return map[priority] || map.medium;
    },

    dateLabel(dateStr) {
        if (!dateStr) return "";
        // Parse MM-DD-YYYY format
        const parts = dateStr.split('-');
        const d = new Date(parseInt(parts[2]), parseInt(parts[0]) - 1, parseInt(parts[1]));
        const now = new Date();
        now.setHours(0, 0, 0, 0);
        const diff = Math.floor((d - now) / 86400000);
        if (diff === 0) return "Today";
        if (diff === 1) return "Tomorrow";
        if (diff === -1) return "Yesterday";
        if (diff > 1 && diff <= 7) return `In ${diff} days`;
        if (diff < -1 && diff >= -7) return `${Math.abs(diff)} days ago`;
        return dateStr;
    },

    isOverdue(dateStr) {
        if (!dateStr) return false;
        const parts = dateStr.split('-');
        const d = new Date(parseInt(parts[2]), parseInt(parts[0]) - 1, parseInt(parts[1]));
        const now = new Date();
        now.setHours(0, 0, 0, 0);
        return d < now;
    },
});
