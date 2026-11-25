import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { QuestionForm } from "@/components/QuestionForm";

describe("QuestionForm", () => {
  it("submits question with filters and role", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<QuestionForm onSubmit={onSubmit} />);

    await user.selectOptions(screen.getByLabelText(/Role/i), "analyst");
    await user.click(screen.getByRole("button", { name: /Ask Analyst/i }));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    expect(onSubmit.mock.calls[0][0].role).toBe("analyst");
    expect(onSubmit.mock.calls[0][0].start_date).toBe("2026-05-01");
  });
});
