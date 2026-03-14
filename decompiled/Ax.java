/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  AA
 *  Ay
 *  Az
 *  com.google.protobuf.ByteString
 *  com.google.protobuf.CodedInputStream
 *  com.google.protobuf.CodedOutputStream
 *  com.google.protobuf.Descriptors$Descriptor
 *  com.google.protobuf.ExtensionRegistryLite
 *  com.google.protobuf.GeneratedMessageV3
 *  com.google.protobuf.GeneratedMessageV3$Builder
 *  com.google.protobuf.GeneratedMessageV3$BuilderParent
 *  com.google.protobuf.GeneratedMessageV3$FieldAccessorTable
 *  com.google.protobuf.GeneratedMessageV3$UnusedPrivateParameter
 *  com.google.protobuf.Internal
 *  com.google.protobuf.InvalidProtocolBufferException
 *  com.google.protobuf.Message
 *  com.google.protobuf.Message$Builder
 *  com.google.protobuf.MessageLite
 *  com.google.protobuf.MessageLite$Builder
 *  com.google.protobuf.Parser
 *  com.google.protobuf.UninitializedMessageException
 *  com.google.protobuf.UnknownFieldSet
 *  com.google.protobuf.UnknownFieldSet$Builder
 *  zS
 */
import com.google.protobuf.ByteString;
import com.google.protobuf.CodedInputStream;
import com.google.protobuf.CodedOutputStream;
import com.google.protobuf.Descriptors;
import com.google.protobuf.ExtensionRegistryLite;
import com.google.protobuf.GeneratedMessageV3;
import com.google.protobuf.Internal;
import com.google.protobuf.InvalidProtocolBufferException;
import com.google.protobuf.Message;
import com.google.protobuf.MessageLite;
import com.google.protobuf.Parser;
import com.google.protobuf.UninitializedMessageException;
import com.google.protobuf.UnknownFieldSet;
import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;

public final class Ax
extends GeneratedMessageV3
implements AA {
    private static final long aqG = 0L;
    int an;
    public static final int aqH = 1;
    long Dj;
    public static final int aqI = 2;
    volatile Object aqJ;
    public static final int aqK = 3;
    volatile Object aqL;
    public static final int aqM = 4;
    long wf;
    private byte Y = (byte)-1;
    private static final Ax aqN = new Ax();
    @Deprecated
    public static final Parser<Ax> aqO = new Ay();

    Ax(GeneratedMessageV3.Builder<?> builder) {
        super(builder);
    }

    private Ax() {
        this.aqJ = "";
        this.aqL = "";
    }

    protected Object newInstance(GeneratedMessageV3.UnusedPrivateParameter unusedPrivateParameter) {
        return new Ax();
    }

    public final UnknownFieldSet getUnknownFields() {
        return this.unknownFields;
    }

    Ax(CodedInputStream codedInputStream, ExtensionRegistryLite extensionRegistryLite) {
        this();
        if (extensionRegistryLite == null) {
            throw new NullPointerException();
        }
        boolean bl = false;
        UnknownFieldSet.Builder builder = UnknownFieldSet.newBuilder();
        try {
            boolean bl2 = false;
            block14: while (!bl2) {
                int n = codedInputStream.readTag();
                switch (n) {
                    case 0: {
                        bl2 = true;
                        continue block14;
                    }
                    case 8: {
                        this.an |= 1;
                        this.Dj = codedInputStream.readInt64();
                        continue block14;
                    }
                    case 18: {
                        ByteString byteString = codedInputStream.readBytes();
                        this.an |= 2;
                        this.aqJ = byteString;
                        continue block14;
                    }
                    case 26: {
                        ByteString byteString = codedInputStream.readBytes();
                        this.an |= 4;
                        this.aqL = byteString;
                        continue block14;
                    }
                    case 32: {
                        this.an |= 8;
                        this.wf = codedInputStream.readInt64();
                        continue block14;
                    }
                }
                if (this.parseUnknownField(codedInputStream, builder, extensionRegistryLite, n)) continue;
                bl2 = true;
            }
        }
        catch (InvalidProtocolBufferException invalidProtocolBufferException) {
            throw invalidProtocolBufferException.setUnfinishedMessage((MessageLite)this);
        }
        catch (UninitializedMessageException uninitializedMessageException) {
            throw uninitializedMessageException.asInvalidProtocolBufferException().setUnfinishedMessage((MessageLite)this);
        }
        catch (IOException iOException) {
            throw new InvalidProtocolBufferException(iOException).setUnfinishedMessage((MessageLite)this);
        }
        finally {
            this.unknownFields = builder.build();
            this.makeExtensionsImmutable();
        }
    }

    public static final Descriptors.Descriptor aDo() {
        return zS.apn;
    }

    protected GeneratedMessageV3.FieldAccessorTable internalGetFieldAccessorTable() {
        return zS.apo.ensureFieldAccessorsInitialized(Ax.class, Az.class);
    }

    public boolean Xh() {
        return (this.an & 1) != 0;
    }

    public long Xi() {
        return this.Dj;
    }

    public boolean aDp() {
        return (this.an & 2) != 0;
    }

    public String aDq() {
        Object object = this.aqJ;
        if (object instanceof String) {
            return (String)object;
        }
        ByteString byteString = (ByteString)object;
        String string = byteString.toStringUtf8();
        if (byteString.isValidUtf8()) {
            this.aqJ = string;
        }
        return string;
    }

    public ByteString aDr() {
        Object object = this.aqJ;
        if (object instanceof String) {
            ByteString byteString = ByteString.copyFromUtf8((String)((String)object));
            this.aqJ = byteString;
            return byteString;
        }
        return (ByteString)object;
    }

    public boolean azs() {
        return (this.an & 4) != 0;
    }

    public String aDs() {
        Object object = this.aqL;
        if (object instanceof String) {
            return (String)object;
        }
        ByteString byteString = (ByteString)object;
        String string = byteString.toStringUtf8();
        if (byteString.isValidUtf8()) {
            this.aqL = string;
        }
        return string;
    }

    public ByteString aDt() {
        Object object = this.aqL;
        if (object instanceof String) {
            ByteString byteString = ByteString.copyFromUtf8((String)((String)object));
            this.aqL = byteString;
            return byteString;
        }
        return (ByteString)object;
    }

    public boolean KT() {
        return (this.an & 8) != 0;
    }

    public long KU() {
        return this.wf;
    }

    public final boolean isInitialized() {
        byte by = this.Y;
        if (by == 1) {
            return true;
        }
        if (by == 0) {
            return false;
        }
        if (!this.Xh()) {
            this.Y = 0;
            return false;
        }
        if (!this.aDp()) {
            this.Y = 0;
            return false;
        }
        this.Y = 1;
        return true;
    }

    public void writeTo(CodedOutputStream codedOutputStream) {
        if ((this.an & 1) != 0) {
            codedOutputStream.writeInt64(1, this.Dj);
        }
        if ((this.an & 2) != 0) {
            GeneratedMessageV3.writeString((CodedOutputStream)codedOutputStream, (int)2, (Object)this.aqJ);
        }
        if ((this.an & 4) != 0) {
            GeneratedMessageV3.writeString((CodedOutputStream)codedOutputStream, (int)3, (Object)this.aqL);
        }
        if ((this.an & 8) != 0) {
            codedOutputStream.writeInt64(4, this.wf);
        }
        this.unknownFields.writeTo(codedOutputStream);
    }

    public int getSerializedSize() {
        int n = this.memoizedSize;
        if (n != -1) {
            return n;
        }
        n = 0;
        if ((this.an & 1) != 0) {
            n += CodedOutputStream.computeInt64Size((int)1, (long)this.Dj);
        }
        if ((this.an & 2) != 0) {
            n += GeneratedMessageV3.computeStringSize((int)2, (Object)this.aqJ);
        }
        if ((this.an & 4) != 0) {
            n += GeneratedMessageV3.computeStringSize((int)3, (Object)this.aqL);
        }
        if ((this.an & 8) != 0) {
            n += CodedOutputStream.computeInt64Size((int)4, (long)this.wf);
        }
        this.memoizedSize = n += this.unknownFields.getSerializedSize();
        return n;
    }

    public boolean equals(Object object) {
        if (object == this) {
            return true;
        }
        if (!(object instanceof Ax)) {
            return super.equals(object);
        }
        Ax ax = (Ax)((Object)object);
        if (this.Xh() != ax.Xh()) {
            return false;
        }
        if (this.Xh() && this.Xi() != ax.Xi()) {
            return false;
        }
        if (this.aDp() != ax.aDp()) {
            return false;
        }
        if (this.aDp() && !this.aDq().equals(ax.aDq())) {
            return false;
        }
        if (this.azs() != ax.azs()) {
            return false;
        }
        if (this.azs() && !this.aDs().equals(ax.aDs())) {
            return false;
        }
        if (this.KT() != ax.KT()) {
            return false;
        }
        if (this.KT() && this.KU() != ax.KU()) {
            return false;
        }
        return this.unknownFields.equals((Object)ax.unknownFields);
    }

    public int hashCode() {
        if (this.memoizedHashCode != 0) {
            return this.memoizedHashCode;
        }
        int n = 41;
        n = 19 * n + Ax.aDo().hashCode();
        if (this.Xh()) {
            n = 37 * n + 1;
            n = 53 * n + Internal.hashLong((long)this.Xi());
        }
        if (this.aDp()) {
            n = 37 * n + 2;
            n = 53 * n + this.aDq().hashCode();
        }
        if (this.azs()) {
            n = 37 * n + 3;
            n = 53 * n + this.aDs().hashCode();
        }
        if (this.KT()) {
            n = 37 * n + 4;
            n = 53 * n + Internal.hashLong((long)this.KU());
        }
        this.memoizedHashCode = n = 29 * n + this.unknownFields.hashCode();
        return n;
    }

    public static Ax ex(ByteBuffer byteBuffer) {
        return (Ax)((Object)aqO.parseFrom(byteBuffer));
    }

    public static Ax cL(ByteBuffer byteBuffer, ExtensionRegistryLite extensionRegistryLite) {
        return (Ax)((Object)aqO.parseFrom(byteBuffer, extensionRegistryLite));
    }

    public static Ax en(ByteString byteString) {
        return (Ax)((Object)aqO.parseFrom(byteString));
    }

    public static Ax cL(ByteString byteString, ExtensionRegistryLite extensionRegistryLite) {
        return (Ax)((Object)aqO.parseFrom(byteString, extensionRegistryLite));
    }

    public static Ax cN(byte[] byArray) {
        return (Ax)((Object)aqO.parseFrom(byArray));
    }

    public static Ax cL(byte[] byArray, ExtensionRegistryLite extensionRegistryLite) {
        return (Ax)((Object)aqO.parseFrom(byArray, extensionRegistryLite));
    }

    public static Ax gw(InputStream inputStream) {
        return (Ax)GeneratedMessageV3.parseWithIOException(aqO, (InputStream)inputStream);
    }

    public static Ax gw(InputStream inputStream, ExtensionRegistryLite extensionRegistryLite) {
        return (Ax)GeneratedMessageV3.parseWithIOException(aqO, (InputStream)inputStream, (ExtensionRegistryLite)extensionRegistryLite);
    }

    public static Ax gx(InputStream inputStream) {
        return (Ax)GeneratedMessageV3.parseDelimitedWithIOException(aqO, (InputStream)inputStream);
    }

    public static Ax gx(InputStream inputStream, ExtensionRegistryLite extensionRegistryLite) {
        return (Ax)GeneratedMessageV3.parseDelimitedWithIOException(aqO, (InputStream)inputStream, (ExtensionRegistryLite)extensionRegistryLite);
    }

    public static Ax cL(CodedInputStream codedInputStream) {
        return (Ax)GeneratedMessageV3.parseWithIOException(aqO, (CodedInputStream)codedInputStream);
    }

    public static Ax kh(CodedInputStream codedInputStream, ExtensionRegistryLite extensionRegistryLite) {
        return (Ax)GeneratedMessageV3.parseWithIOException(aqO, (CodedInputStream)codedInputStream, (ExtensionRegistryLite)extensionRegistryLite);
    }

    public Az aDu() {
        return Ax.aDv();
    }

    public static Az aDv() {
        return aqN.aDw();
    }

    public static Az a(Ax ax) {
        return aqN.aDw().c(ax);
    }

    public Az aDw() {
        return this == aqN ? new Az() : new Az().c(this);
    }

    protected Az cL(GeneratedMessageV3.BuilderParent builderParent) {
        Az az = new Az(builderParent);
        return az;
    }

    public static Ax aDx() {
        return aqN;
    }

    public static Parser<Ax> z() {
        return aqO;
    }

    public Parser<Ax> getParserForType() {
        return aqO;
    }

    public Ax aDy() {
        return aqN;
    }

    protected /* synthetic */ Message.Builder newBuilderForType(GeneratedMessageV3.BuilderParent builderParent) {
        return this.cL(builderParent);
    }

    public /* synthetic */ Message.Builder toBuilder() {
        return this.aDw();
    }

    public /* synthetic */ Message.Builder newBuilderForType() {
        return this.aDu();
    }

    public /* synthetic */ MessageLite.Builder toBuilder() {
        return this.aDw();
    }

    public /* synthetic */ MessageLite.Builder newBuilderForType() {
        return this.aDu();
    }

    public /* synthetic */ MessageLite getDefaultInstanceForType() {
        return this.aDy();
    }

    public /* synthetic */ Message getDefaultInstanceForType() {
        return this.aDy();
    }

    static /* synthetic */ boolean Y() {
        return alwaysUseFieldBuilders;
    }

    static /* synthetic */ UnknownFieldSet b(Ax ax) {
        return ax.unknownFields;
    }
}
