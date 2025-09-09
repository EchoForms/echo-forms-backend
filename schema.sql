-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS users_id_seq;

-- Table Definition
CREATE TABLE "public"."users" (
    "id" int4 NOT NULL DEFAULT nextval('users_id_seq'::regclass),
    "username" varchar(50) NOT NULL,
    "email" varchar(100) NOT NULL,
    "password" varchar(255) NOT NULL,
    "role" varchar(20) NOT NULL DEFAULT 'user'::character varying,
    "subscription" varchar(255) NOT NULL DEFAULT 'free'::character varying,
    "status" varchar(255) NOT NULL DEFAULT 'active'::character varying,
    "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "name" varchar(255),
    PRIMARY KEY ("id")
);


-- Indices
CREATE UNIQUE INDEX users_username_key ON public.users USING btree (username);
CREATE UNIQUE INDEX users_email_key ON public.users USING btree (email);

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS forms_id_seq;

-- Table Definition
CREATE TABLE "public"."forms" (
    "id" int4 NOT NULL DEFAULT nextval('forms_id_seq'::regclass),
    "title" varchar(255) NOT NULL,
    "description" text,
    "user_id" int4 NOT NULL,
    "language" varchar(50),
    "status" varchar(20) NOT NULL,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    "is_public" int4,
    "form_unique_id" varchar(36) NOT NULL,
    CONSTRAINT "forms_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id"),
    PRIMARY KEY ("id")
);


-- Indices
CREATE INDEX ix_forms_id ON public.forms USING btree (id);
CREATE UNIQUE INDEX forms_form_unique_id_key ON public.forms USING btree (form_unique_id);

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS form_fields_id_seq;

-- Table Definition
CREATE TABLE "public"."form_fields" (
    "id" int4 NOT NULL DEFAULT nextval('form_fields_id_seq'::regclass),
    "question" varchar(255) NOT NULL,
    "required" bool,
    "form_id" int4 NOT NULL,
    "options" json,
    "status" varchar(20) NOT NULL,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    "question_number" int4 NOT NULL DEFAULT 1,
    "user_id" int4,
    CONSTRAINT "form_fields_form_id_fkey" FOREIGN KEY ("form_id") REFERENCES "public"."forms"("id"),
    CONSTRAINT "fk_form_fields_user_id" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id"),
    PRIMARY KEY ("id")
);


-- Indices
CREATE INDEX ix_form_fields_id ON public.form_fields USING btree (id);

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS "form_responses_responseId_seq";

-- Table Definition
CREATE TABLE "public"."form_responses" (
    "responseId" int4 NOT NULL DEFAULT nextval('"form_responses_responseId_seq"'::regclass),
    "formId" int4 NOT NULL,
    "created_at" timestamp NOT NULL DEFAULT now(),
    "updated_at" timestamp NOT NULL DEFAULT now(),
    "status" varchar(32) NOT NULL DEFAULT 'in_progress'::character varying,
    "submitTimestamp" timestamp,
    "language" varchar(10) DEFAULT 'en',
    "user_id" int4,
    CONSTRAINT "fk_form_responses_user_id" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id"),
    CONSTRAINT "form_responses_formId_fkey" FOREIGN KEY ("formId") REFERENCES "public"."forms"("id"),
    PRIMARY KEY ("responseId")
);


-- Indices
CREATE INDEX "ix_form_responses_responseId" ON public.form_responses USING btree ("responseId");

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS "form_response_fields_responsefieldId_seq";

-- Table Definition
CREATE TABLE "public"."form_response_fields" (
    "responsefieldId" int4 NOT NULL DEFAULT nextval('"form_response_fields_responsefieldId_seq"'::regclass),
    "formResponseId" int4 NOT NULL,
    "formId" int4 NOT NULL,
    "formfeildId" int4 NOT NULL,
    "responseText" text,
    "voiceFileLink" varchar(255),
    "response_time" float8,
    "transcribed_text" text,
    "translated_text" text,
    "categories" json,
    "sentiment" varchar(20) DEFAULT 'neutral',
    "user_id" int4,
    CONSTRAINT "form_response_fields_formfeildId_fkey" FOREIGN KEY ("formfeildId") REFERENCES "public"."form_fields"("id") ON DELETE CASCADE,
    CONSTRAINT "form_response_fields_formResponseId_fkey" FOREIGN KEY ("formResponseId") REFERENCES "public"."form_responses"("responseId") ON DELETE CASCADE,
    CONSTRAINT "fk_form_response_fields_user_id" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id"),
    CONSTRAINT "form_response_fields_formId_fkey" FOREIGN KEY ("formId") REFERENCES "public"."forms"("id") ON DELETE CASCADE,
    PRIMARY KEY ("responsefieldId")
);

-- Indices
CREATE INDEX "ix_form_response_fields_responsefieldId" ON public.form_response_fields USING btree ("responsefieldId");

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS "form_analytics_analyticsId_seq";

-- Table Definition
CREATE TABLE "public"."form_analytics" (
    "analyticsId" int4 NOT NULL DEFAULT nextval('"form_analytics_analyticsId_seq"'::regclass),
    "formId" int4 NOT NULL,
    "response_categories" json,
    "total_responses" int4 DEFAULT 0,
    "create_timestamp" timestamp DEFAULT now(),
    "update_timestamp" timestamp DEFAULT now(),
    "status" varchar(20) NOT NULL DEFAULT 'active'::character varying,
    CONSTRAINT "form_analytics_formId_fkey" FOREIGN KEY ("formId") REFERENCES "public"."forms"("id") ON DELETE CASCADE,
    PRIMARY KEY ("analyticsId")
);

-- Indices
CREATE INDEX "ix_form_analytics_analyticsId" ON public.form_analytics USING btree ("analyticsId");
CREATE INDEX "ix_form_analytics_formId" ON public.form_analytics USING btree ("formId");

