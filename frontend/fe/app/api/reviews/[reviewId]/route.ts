import { NextResponse } from "next/server";

const reviewStore = new Map<string, Record<string, unknown>>();

export async function GET(
  request: Request,
  { params }: { params: Promise<{ reviewId: string }> },
) {
  const { reviewId } = await params;
  const item = reviewStore.get(reviewId);

  if (!item) {
    return NextResponse.json({ error: "Review not found" }, { status: 404 });
  }

  return NextResponse.json(item);
}
