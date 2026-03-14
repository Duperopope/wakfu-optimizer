import { NextResponse } from "next/server";
import { readFileSync, existsSync } from "fs";
import { join } from "path";

const DATA_DIR = join(process.cwd(), "..", "data", "wakfuli");

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const file = searchParams.get("file");

  if (!file || !/^[a-z_]+\.json$/.test(file)) {
    return NextResponse.json({ error: "Invalid file parameter" }, { status: 400 });
  }

  const filePath = join(DATA_DIR, file);

  if (!existsSync(filePath)) {
    return NextResponse.json({ error: `File not found: ${file}` }, { status: 404 });
  }

  try {
    const raw = readFileSync(filePath, "utf-8");
    const data = JSON.parse(raw);
    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json({ error: "Failed to parse file" }, { status: 500 });
  }
}
