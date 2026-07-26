from __future__ import annotations
from supabase import create_client, Client

from typing import Any

from app.config import settings


class SupabaseClient:
    def __init__(self) -> None:
        self.base_url = settings.supabase_url
        self.api_key = settings.supabase_key
        
        self.client: Client = create_client(self.base_url, self.api_key)

    async def insert(self, table_name: str, data: dict[str, Any]) -> dict[str, Any]:
        """Insert a single record into a table"""
        try:
            response = (
                self.client
                .table(table_name)
                .insert(data)
                .execute()
            )
            return response.data
        except Exception as e:
            raise Exception(f"Error inserting into {table_name}: {str(e)}")

    async def select(self, table_name: str, filters: dict[str, Any] | None = None, match_type: str = "exact") -> list[dict[str, Any]]:
        """Select records from a table with optional filters
        
        Args:
            table_name: Name of the table to query
            filters: Dictionary of column-value pairs to filter by
            match_type: "exact" for exact match (default) or "partial" for case-insensitive partial match
        """
        try:
            query = self.client.table(table_name).select("*")
            
            if filters:
                for key, value in filters.items():
                    if match_type == "partial":
                        query = query.ilike(key, f"%{value}%")
                    else:  # exact match
                        query = query.eq(key, value)
            
            response = query.execute()
            return response.data
        except Exception as e:
            raise Exception(f"Error selecting from {table_name}: {str(e)}")

    async def update(self, table_name: str, data: dict[str, Any], filters: dict[str, Any], match_type: str = "exact") -> dict[str, Any]:
        """Update records in a table based on filters"""
        try:
            client = self.client.table(table_name)
            select_query = client.select("*")

            if filters:
                for key, value in filters.items():
                    if match_type == "partial":
                        select_query = select_query.ilike(key, f"%{value}%")
                    else:  # exact match
                        select_query = select_query.eq(key, value)
            select_response = select_query.execute()
            records = select_response.data or []

            if not records:
                raise Exception(f"No matching records found in {table_name} for filters {filters}")

            latest_record = max(records, key=lambda record: record.get("created_at", ""))
            conversation_id = latest_record.get("conversation_id")

            if conversation_id is None:
                raise Exception("Latest record is missing conversation_id")

            update_query = client.update(data).eq("conversation_id", conversation_id)
            updated_response = update_query.execute()
            return updated_response.data
        except Exception as e:
            raise Exception(f"Error updating {table_name}: {str(e)}")

    async def delete(self, table_name: str, filters: dict[str, Any]) -> dict[str, Any]:
        """Delete records from a table based on filters"""
        try:
            query = self.client.table(table_name)
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.delete().execute()
            return response.data
        except Exception as e:
            raise Exception(f"Error deleting from {table_name}: {str(e)}")

    async def close(self) -> None:
        """Close the client connection"""
        pass