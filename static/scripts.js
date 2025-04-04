function addOperation(containerId) {
  const container = document.getElementById(containerId);
  const div = document.createElement("div");
  div.className = "operation";
  div.innerHTML = `
        <input type="text" placeholder="Descripción" required>
        <input type="text" placeholder="Código" required>
        <input type="number" placeholder="Precio" step="0.01" required>
        <input type="number" placeholder="Cantidad">
        <input type="checkbox"> Exento
    `;
  container.appendChild(div);
}

function addGood(containerId) {
  const container = document.getElementById(containerId);
  const input = document.createElement("input");
  input.type = "text";
  input.className = "good";
  input.placeholder = "Bien entregado";
  input.required = true;
  container.appendChild(input);
}

async function submitForm(event, endpoint) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  let jsonData = {};

  // No incluimos emisor en el payload, se usará el predeterminado en el backend
  jsonData.receptor = {
    name: formData.get("receptor_name"),
    fiscal_address: formData.get("receptor_fiscal_address"),
    rif: formData.get("receptor_rif") || null,
    id_number: formData.get("receptor_id_number") || null,
  };

  jsonData.issuance_date = formData.get("issuance_date");
  jsonData.issuance_time = formData.get("issuance_time");
  jsonData.digital_printer_id = parseInt(formData.get("digital_printer_id"));

  if (
    endpoint.includes("facturas") ||
    endpoint.includes("debit_notes") ||
    endpoint.includes("credit_notes")
  ) {
    jsonData.operations = [];
    const operations = form.querySelectorAll(".operation");
    operations.forEach((op) => {
      jsonData.operations.push({
        description: op.querySelector("input:nth-child(1)").value,
        code: op.querySelector("input:nth-child(2)").value,
        price: parseFloat(op.querySelector("input:nth-child(3)").value),
        quantity: op.querySelector("input:nth-child(4)").value
          ? parseInt(op.querySelector("input:nth-child(4)").value)
          : null,
        is_exempt: op.querySelector("input:nth-child(5)").checked,
      });
    });
  }

  if (endpoint.includes("delivery_orders")) {
    jsonData.goods_delivered = [];
    const goods = form.querySelectorAll(".good");
    goods.forEach((good) => jsonData.goods_delivered.push(good.value));
  }

  if (
    endpoint.includes("debit_notes") ||
    endpoint.includes("credit_notes") ||
    endpoint.includes("retention_receipts")
  ) {
    jsonData.related_document_id = parseInt(
      formData.get("related_document_id")
    );
  }

  if (endpoint.includes("retention_receipts")) {
    jsonData.tax_type = formData.get("tax_type");
    jsonData.retained_amount = parseFloat(formData.get("retained_amount"));
  }

  try {
    const response = await fetch(`/${endpoint}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(jsonData),
    });
    if (response.ok) {
      const result = await response.json();
      alert("Documento creado con éxito: " + JSON.stringify(result));
    } else {
      const error = await response.json();
      alert("Error: " + JSON.stringify(error));
    }
  } catch (error) {
    alert("Error al enviar la solicitud: " + error.message);
  }
}

async function submitMaintenanceForm(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  const jsonData = {
    name: formData.get("name"),
    fiscal_address: formData.get("fiscal_address"),
    rif: formData.get("rif"),
  };

  try {
    const response = await fetch("/maintenance/update_emisor", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(jsonData),
    });
    if (response.ok) {
      const html = await response.text();
      document.body.innerHTML = html;
    } else {
      const error = await response.json();
      alert("Error: " + JSON.stringify(error));
    }
  } catch (error) {
    alert("Error al enviar la solicitud: " + error.message);
  }
}
