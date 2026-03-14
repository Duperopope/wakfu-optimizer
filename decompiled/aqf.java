/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  org.apache.log4j.Logger
 */
import org.apache.log4j.Logger;

public final class aqf
extends apW {
    private static final Logger cQq = Logger.getLogger(aqf.class);
    private static final aqf cQr = new aqf();

    public static aqf bGr() {
        return cQr;
    }

    private aqf() {
        super("data.bdat", "indexes.bdat", true);
        this.setName("SimpleBinaryStorage");
    }

    public aqf(String string) {
        super("data.bdat", "indexes.bdat", true);
        this.setName(string);
    }
}
