import React, { useEffect } from "react";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// Utility function to get today's date in YYYY-MM-DD
const getToday = () => {
  const today = new Date();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");
  return `${today.getFullYear()}-${month}-${day}`;
};

const ExpenseNotifications = ({ expenses }) => {
  useEffect(() => {
    const today = getToday();
    const dueExpenses = expenses.filter((expense) => expense.date === today);

    if (dueExpenses.length > 0) {
      dueExpenses.forEach((expense) => {
        toast.info(
          `Expense due today: ${expense.title} - Rs.${expense.amount.toLocaleString()}`,
          {
            position: "top-right",
            autoClose: 5000,
            hideProgressBar: false,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
          }
        );
      });
    }
  }, [expenses]); // Listen for changes to expenses

  return <ToastContainer />;
};

export default ExpenseNotifications;