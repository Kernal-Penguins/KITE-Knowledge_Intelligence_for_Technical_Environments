export type EquipmentStatus = "Operational" | "Warning" | "Failed";

export interface Equipment {
  id: string;
  tag: string;
  type: string;
  cluster: "Rotating Equipment" | "Piping & Instrumentation" | "Electrical Systems";
  status: EquipmentStatus;
}

export interface Document {
  id: string;
  filename: string;
  docType: string;
  ingestedAt: string;
  status: "Complete" | "Processing" | "Needs Review";
  linkedEquipment: string[];
  preview: string;
}

export interface Relationship {
  from: string;
  to: string;
  type: string;
}

export interface ReviewCandidate {
  id: string;
  entityA: string;
  entityB: string;
  entityType: string;
  confidence: number;
  source: string;
}

export const equipment: Equipment[] = [
  { id: "eq-p101", tag: "P-101", type: "Centrifugal Pump", cluster: "Rotating Equipment", status: "Failed" },
  { id: "eq-v205", tag: "V-205", type: "Control Valve", cluster: "Piping & Instrumentation", status: "Operational" },
  { id: "eq-hx310", tag: "HX-310", type: "Heat Exchanger", cluster: "Rotating Equipment", status: "Operational" },
  { id: "eq-mot118", tag: "MOT-118", type: "Drive Motor", cluster: "Electrical Systems", status: "Warning" },
  { id: "eq-tk04", tag: "TK-04", type: "Storage Tank", cluster: "Piping & Instrumentation", status: "Operational" },
];

export const documents: Document[] = [
  {
    id: "doc-1",
    filename: "maintenance_log_P-101.docx",
    docType: "Maintenance Log",
    ingestedAt: "2026-05-12",
    status: "Complete",
    linkedEquipment: ["eq-p101"],
    preview:
      "Maintenance Log for P-101\n\nOn 2026-05-12, the pump seal was found to be leaking heavily.\nAction taken: replaced seal and tested.",
  },
  {
    id: "doc-2",
    filename: "inspection_report_V-205.pdf",
    docType: "Inspection Report",
    ingestedAt: "2026-05-13",
    status: "Complete",
    linkedEquipment: ["eq-v205"],
    preview: "Inspection Report\n\nEquipment V-205 was inspected on 2026-05-13. No leaks found.",
  },
  {
    id: "doc-3",
    filename: "equipment_status_export.csv",
    docType: "Status Export",
    ingestedAt: "2026-05-11",
    status: "Complete",
    linkedEquipment: ["eq-p101", "eq-v205"],
    preview: "Equipment, Status, Date\nP-101, Failed, 2026-05-10\nV-205, Operational, 2026-05-11",
  },
  {
    id: "doc-4",
    filename: "vendor_manual_HX-310.pdf",
    docType: "Vendor Manual",
    ingestedAt: "2026-05-09",
    status: "Processing",
    linkedEquipment: ["eq-hx310"],
    preview: "Heat exchanger service manual -- shell-and-tube cleaning interval, gasket torque spec...",
  },
  {
    id: "doc-5",
    filename: "electrical_schematics_MOT-118.pdf",
    docType: "Schematic",
    ingestedAt: "2026-05-08",
    status: "Needs Review",
    linkedEquipment: ["eq-mot118"],
    preview: "Drive motor MOT-118 wiring diagram -- three-phase supply, thermal overload trip at 42A...",
  },
];

export const relationships: Relationship[] = [
  { from: "eq-p101", to: "doc-1", type: "HAS_LOG" },
  { from: "eq-v205", to: "doc-2", type: "HAS_REPORT" },
  { from: "doc-3", to: "eq-p101", type: "REFERENCES" },
  { from: "doc-3", to: "eq-v205", type: "REFERENCES" },
  { from: "eq-p101", to: "eq-v205", type: "CONNECTED_TO" },
  { from: "eq-v205", to: "eq-tk04", type: "CONNECTED_TO" },
  { from: "eq-hx310", to: "eq-p101", type: "CONNECTED_TO" },
  { from: "eq-mot118", to: "eq-p101", type: "DRIVES" },
];

export const reviewQueue: ReviewCandidate[] = [
  { id: "rc-1", entityA: "P-101", entityB: "Pump P-101", entityType: "Equipment", confidence: 0.94, source: "equipment_status_export.csv" },
  { id: "rc-2", entityA: "V-205", entityB: "Valve-205", entityType: "Equipment", confidence: 0.88, source: "inspection_report_V-205.pdf" },
  { id: "rc-3", entityA: "HX-310", entityB: "Heat Exchanger 310", entityType: "Equipment", confidence: 0.81, source: "vendor_manual_HX-310.pdf" },
  { id: "rc-4", entityA: "MOT-118", entityB: "Motor-118A", entityType: "Equipment", confidence: 0.76, source: "electrical_schematics_MOT-118.pdf" },
];

export const stats = {
  entitiesMapped: 8412,
  entityTypes: 34,
  relationshipsTraced: 24905,
  pendingReview: 156,
};
