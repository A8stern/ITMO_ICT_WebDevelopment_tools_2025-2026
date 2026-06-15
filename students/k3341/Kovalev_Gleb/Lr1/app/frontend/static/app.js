const state = {
  token: localStorage.getItem("finance_token") || "",
  categories: [],
  tags: [],
  transactions: [],
  budgets: [],
  goals: [],
  notifications: []
};

const statusLine = document.querySelector("#statusLine");

function setStatus(message) {
  statusLine.textContent = message;
}

function getFormData(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function numberValue(value) {
  return value === "" || value === null ? null : Number(value);
}

async function request(path, options = {}) {
  const headers = {"Content-Type": "application/json", ...(options.headers || {})};
  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }
  const response = await fetch(path, {...options, headers});
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;
  if (!response.ok) {
    throw new Error(data?.detail || "Request failed");
  }
  return data;
}

function formatMoney(value) {
  return new Intl.NumberFormat("ru-RU", {maximumFractionDigits: 0}).format(value || 0);
}

function fillSelect(select, items, getLabel) {
  select.innerHTML = "";
  for (const item of items) {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = getLabel(item);
    select.append(option);
  }
}

function renderChips(target, items, getText) {
  target.innerHTML = "";
  for (const item of items) {
    const chip = document.createElement("div");
    chip.className = "chip";
    chip.textContent = getText(item);
    target.append(chip);
  }
}

function renderList(target, items, getText) {
  target.innerHTML = "";
  for (const item of items) {
    const node = document.createElement("div");
    node.className = "list-item";
    node.textContent = getText(item);
    target.append(node);
  }
}

function renderTransactions() {
  const table = document.querySelector("#transactionsTable");
  table.innerHTML = "";
  for (const item of state.transactions) {
    const row = document.createElement("tr");
    const tags = item.tags?.map((tag) => tag.name).join(", ") || "";
    row.innerHTML = `
      <td>${item.title}</td>
      <td>${item.transaction_type}</td>
      <td>${formatMoney(item.amount)}</td>
      <td>${item.category?.title || "Без категории"}</td>
      <td>${tags || "Нет тегов"}</td>
    `;
    table.append(row);
  }
}

function renderAll() {
  fillSelect(document.querySelector("#transactionCategorySelect"), state.categories, (item) => item.title);
  fillSelect(document.querySelector("#budgetCategorySelect"), state.categories, (item) => item.title);
  fillSelect(document.querySelector("#linkTransactionSelect"), state.transactions, (item) => item.title);
  fillSelect(document.querySelector("#linkTagSelect"), state.tags, (item) => item.name);
  renderChips(document.querySelector("#categoriesList"), state.categories, (item) => `${item.title}: ${formatMoney(item.monthly_limit)}`);
  renderChips(document.querySelector("#tagsList"), state.tags, (item) => item.name);
  renderTransactions();
  renderList(document.querySelector("#budgetsList"), state.budgets, (item) => `${item.title}: ${formatMoney(item.amount)}`);
  renderList(document.querySelector("#goalsList"), state.goals, (item) => `${item.title}: ${formatMoney(item.current_amount)} / ${formatMoney(item.target_amount)}`);
  renderList(document.querySelector("#notificationsList"), state.notifications, (item) => `${item.title}: ${item.message}`);
}

async function refreshData() {
  if (!state.token) {
    setStatus("Сначала войдите или зарегистрируйтесь");
    renderAll();
    return;
  }
  const [categories, tags, transactions, budgets, goals, notifications, report] = await Promise.all([
    request("/categories_list"),
    request("/tags_list"),
    request("/transactions_list"),
    request("/budgets_list"),
    request("/goals_list"),
    request("/notifications_list"),
    request("/report")
  ]);
  state.categories = categories;
  state.tags = tags;
  state.transactions = transactions;
  state.budgets = budgets;
  state.goals = goals;
  state.notifications = notifications;
  document.querySelector("#incomeValue").textContent = formatMoney(report.total_income);
  document.querySelector("#expenseValue").textContent = formatMoney(report.total_expense);
  document.querySelector("#balanceValue").textContent = formatMoney(report.balance);
  document.querySelector("#notificationsValue").textContent = report.unread_notifications_count;
  renderAll();
  setStatus("Данные обновлены");
}

async function submitJson(form, path, buildBody) {
  const body = buildBody(getFormData(form));
  await request(path, {method: "POST", body: JSON.stringify(body)});
  form.reset();
  await refreshData();
}

document.querySelector("#registerForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await request("/auth/register", {method: "POST", body: JSON.stringify(getFormData(event.currentTarget))});
    setStatus("Пользователь создан, теперь можно войти");
  } catch (error) {
    setStatus(error.message);
  }
});

document.querySelector("#loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const data = await request("/auth/login", {method: "POST", body: JSON.stringify(getFormData(event.currentTarget))});
    state.token = data.access_token;
    localStorage.setItem("finance_token", state.token);
    setStatus("Вход выполнен");
    await refreshData();
  } catch (error) {
    setStatus(error.message);
  }
});

document.querySelector("#logoutButton").addEventListener("click", () => {
  state.token = "";
  localStorage.removeItem("finance_token");
  setStatus("Вы вышли из аккаунта");
});

document.querySelector("#refreshButton").addEventListener("click", () => {
  refreshData().catch((error) => setStatus(error.message));
});

document.querySelector("#categoryForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await submitJson(event.currentTarget, "/category", (data) => ({
      title: data.title,
      description: data.description,
      monthly_limit: numberValue(data.monthly_limit)
    }));
  } catch (error) {
    setStatus(error.message);
  }
});

document.querySelector("#tagForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await submitJson(event.currentTarget, "/tag", (data) => ({
      name: data.name,
      description: data.description
    }));
  } catch (error) {
    setStatus(error.message);
  }
});

document.querySelector("#transactionForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await submitJson(event.currentTarget, "/transaction", (data) => ({
      transaction_type: data.transaction_type,
      title: data.title,
      amount: numberValue(data.amount),
      operation_date: data.operation_date,
      description: data.description,
      category_id: numberValue(data.category_id)
    }));
  } catch (error) {
    setStatus(error.message);
  }
});

document.querySelector("#linkForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await submitJson(event.currentTarget, "/transaction_tag", (data) => ({
      transaction_id: numberValue(data.transaction_id),
      tag_id: numberValue(data.tag_id),
      importance_level: numberValue(data.importance_level)
    }));
  } catch (error) {
    setStatus(error.message);
  }
});

document.querySelector("#budgetForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await submitJson(event.currentTarget, "/budget", (data) => ({
      title: data.title,
      amount: numberValue(data.amount),
      period_start: data.period_start,
      period_end: data.period_end,
      category_id: numberValue(data.category_id)
    }));
  } catch (error) {
    setStatus(error.message);
  }
});

document.querySelector("#goalForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await submitJson(event.currentTarget, "/goal", (data) => ({
      title: data.title,
      target_amount: numberValue(data.target_amount),
      current_amount: numberValue(data.current_amount),
      deadline: data.deadline,
      is_completed: false
    }));
  } catch (error) {
    setStatus(error.message);
  }
});

document.querySelector("#notificationForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await submitJson(event.currentTarget, "/notification", (data) => ({
      title: data.title,
      message: data.message,
      is_read: false
    }));
  } catch (error) {
    setStatus(error.message);
  }
});

renderAll();
refreshData().catch(() => setStatus("Готов к тестовой работе через отдельную среду"));
