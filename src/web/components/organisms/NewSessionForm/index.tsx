import { zodResolver } from "@hookform/resolvers/zod";
import { JSX } from "react";
import { useForm, useWatch } from "react-hook-form";
import * as z from "zod";

import Button from "@/components/atoms/Button";
import Heading from "@/components/atoms/Heading";
import CheckboxField from "@/components/molecules/CheckboxField";
import InputField from "@/components/molecules/InputField";
import SelectField from "@/components/molecules/SelectField";
import TextareaField from "@/components/molecules/TextareaField";

import {
  formContainer,
  fieldsetContainer,
  legendStyle,
  hyperparametersGrid,
  errorMessageStyle,
} from "./style.css";

const formSchema = z.object({
  purpose: z.string().min(1, "Purpose is required"),
  background: z.string().min(1, "Background is required"),
  roles: z.string().optional(),
  parent: z.string().optional(),
  references: z.string().optional(),
  artifacts: z.string().optional(),
  procedure: z.string().optional(),
  instruction: z.string().min(1, "First Instruction is required"),
  multi_step_reasoning_enabled: z.boolean().default(false),
  hyperparameters: z
    .object({
      temperature: z.number().min(0).max(2).default(0.7),
      top_p: z.number().min(0).max(1).default(0.9),
      top_k: z.number().min(1).max(50).default(5),
    })
    .optional(),
});

type NewSessionFormInputs = z.infer<typeof formSchema>;

type DefaultSettings = {
  parameters?: {
    temperature?: { value: number };
    top_p?: { value: number };
    top_k?: { value: number };
  };
};

type NewSessionFormProps = {
  onSubmit: (data: NewSessionFormInputs) => void;
  sessions: { value: string; label: string }[];
  defaultSettings: DefaultSettings;
};

const NewSessionForm: ({
  onSubmit,
  sessions,
  defaultSettings,
}: NewSessionFormProps) => JSX.Element = ({ onSubmit, sessions, defaultSettings }) => {
  const {
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
  } = useForm<NewSessionFormInputs>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      purpose: "",
      background: "",
      roles: "",
      parent: "",
      references: "",
      artifacts: "",
      procedure: "",
      instruction: "",
      multi_step_reasoning_enabled: false,
      hyperparameters: {
        temperature: defaultSettings.parameters?.temperature?.value || 0.7,
        top_p: defaultSettings.parameters?.top_p?.value || 0.9,
        top_k: defaultSettings.parameters?.top_k?.value || 5,
      },
    },
  });

  const temperatureValue = useWatch({ control, name: "hyperparameters.temperature" });
  const topPValue = useWatch({ control, name: "hyperparameters.top_p" });
  const topKValue = useWatch({ control, name: "hyperparameters.top_k" });

  const parentSessionOptions = [{ value: "", label: "None" }, ...sessions];

  return (
    <div className={formContainer}>
      <Heading level={1}>Create New Chat Session</Heading>
      <form onSubmit={handleSubmit(onSubmit)}>
        <InputField
          control={control}
          name="purpose"
          label="Purpose:"
          id="purpose"
          required
        />
        <TextareaField
          control={control}
          name="background"
          label="Background:"
          id="background"
          required
        />
        <InputField
          control={control}
          name="roles"
          label="Roles (comma-separated paths, e.g., roles/engineer.md):"
          id="roles"
        />
        <SelectField
          control={control}
          name="parent"
          label="Parent Session (optional):"
          id="parent"
          options={parentSessionOptions}
        />
        <InputField
          control={control}
          name="references"
          label="References (comma-separated paths):"
          id="references"
        />
        <InputField
          control={control}
          name="artifacts"
          label="Artifacts (comma-separated paths):"
          id="artifacts"
        />
        <InputField
          control={control}
          name="procedure"
          label="Procedure (path to file):"
          id="procedure"
        />
        <TextareaField
          control={control}
          name="instruction"
          label="First Instruction:"
          id="instruction"
          required
        />
        <CheckboxField
          control={control}
          name="multi_step_reasoning_enabled"
          label="Enable Multi-step Reasoning"
          id="multi-step-reasoning"
        />

        <fieldset className={fieldsetContainer}>
          <legend className={legendStyle}>Hyperparameters</legend>
          <div className={hyperparametersGrid}>
            <InputField
              control={control}
              name="hyperparameters.temperature"
              label={`Temperature: ${temperatureValue}`}
              id="temperature"
              type="range"
              min="0"
              max="2"
              step="0.1"
            />
            <InputField
              control={control}
              name="hyperparameters.top_p"
              label={`Top P: ${topPValue}`}
              id="top_p"
              type="range"
              min="0"
              max="1"
              step="0.1"
            />
            <InputField
              control={control}
              name="hyperparameters.top_k"
              label={`Top K: ${topKValue}`}
              id="top_k"
              type="range"
              min="1"
              max="50"
              step="1"
            />
          </div>
        </fieldset>

        <Button type="submit" kind="primary" size="default" disabled={isSubmitting}>
          {isSubmitting ? "Creating..." : "Create Session"}
        </Button>
        <Button
          type="button"
          kind="secondary"
          size="default"
          onClick={() => (window.location.href = "/")}
        >
          Cancel
        </Button>
        {Object.keys(errors).length > 0 && (
          <p className={errorMessageStyle}>Please correct the errors in the form.</p>
        )}
      </form>
    </div>
  );
};

export default NewSessionForm;
